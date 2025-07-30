"""
replayed.models.bsor
--------------------

Main model for a BSOR (Beat Saber Replay) file.
"""
import logging
from typing import BinaryIO, List, Optional, Dict, Any, Callable
from pydantic import Field

from ..base_types import PydanticWritableBase, BSException
from ..io_utils import (
    decode_int, decode_byte, encode_int, encode_byte,
    write_list # Using the new generic list writer
)
from ..utils import make_list_from_stream # Using new generic list reader
from ..constants import (
    BSOR_MAGIC_NUMBER_INT, BSOR_MAGIC_NUMBER_HEX, MAX_SUPPORTED_BSOR_VERSION,
    FRAMES_MAGIC_BYTE, NOTES_MAGIC_BYTE, WALLS_MAGIC_BYTE, HEIGHTS_MAGIC_BYTE,
    PAUSES_MAGIC_BYTE, CONTROLLER_OFFSETS_MAGIC_BYTE, USER_DATA_MAGIC_BYTE
)

from .info import Info
from .frame import Frame
from .note import Note
from .wall import Wall
from .height import HeightEvent
from .pause import Pause
from .controller_offsets import ControllerOffsets
from .user_data import UserDataEntry


class Bsor(PydanticWritableBase):
    """Represents the entire content of a BSOR replay file."""
    magic_number: int = Field(default=BSOR_MAGIC_NUMBER_INT)
    file_version: int = Field(default=MAX_SUPPORTED_BSOR_VERSION) # BSOR spec version
    
    info: Info = Field(default_factory=Info)
    frames: List[Frame] = Field(default_factory=list)
    notes: List[Note] = Field(default_factory=list)
    walls: List[Wall] = Field(default_factory=list)
    heights: List[HeightEvent] = Field(default_factory=list)
    pauses: List[Pause] = Field(default_factory=list)
    
    # Optional sections (appeared in later BSOR versions or extensions)
    controller_offsets: Optional[ControllerOffsets] = Field(default=None)
    user_data: List[UserDataEntry] = Field(default_factory=list) # UserData section can have multiple entries

    def write(self, f: BinaryIO) -> None:
        encode_int(f, self.magic_number)
        encode_byte(f, self.file_version)
        
        self.info.write(f) # Info has its own magic byte handling internally

        # For lists, use the generic writer with specific item writers
        write_list(f, self.frames, lambda s, item: item.write(s), write_magic_byte=FRAMES_MAGIC_BYTE)
        write_list(f, self.notes, lambda s, item: item.write(s), write_magic_byte=NOTES_MAGIC_BYTE)
        write_list(f, self.walls, lambda s, item: item.write(s), write_magic_byte=WALLS_MAGIC_BYTE)
        write_list(f, self.heights, lambda s, item: item.write(s), write_magic_byte=HEIGHTS_MAGIC_BYTE)
        write_list(f, self.pauses, lambda s, item: item.write(s), write_magic_byte=PAUSES_MAGIC_BYTE)

        if self.controller_offsets is not None:
            encode_byte(f, CONTROLLER_OFFSETS_MAGIC_BYTE)
            self.controller_offsets.write(f)
        
        if self.user_data: # Only write if there's data
             write_list(f, self.user_data, lambda s, item: item.write(s), write_magic_byte=USER_DATA_MAGIC_BYTE)


    @classmethod
    def from_stream(cls, f: BinaryIO) -> "Bsor":
        magic = decode_int(f)
        if magic != BSOR_MAGIC_NUMBER_INT:
            # Original compared hex strings, but int comparison is fine.
            # hex(magic) vs BSOR_MAGIC_NUMBER_HEX
            raise BSException(f"File magic number mismatch. Expected {BSOR_MAGIC_NUMBER_INT} ({BSOR_MAGIC_NUMBER_HEX}), got {magic} ({hex(magic)}).")

        version = decode_byte(f)
        if version > MAX_SUPPORTED_BSOR_VERSION:
            logging.warning(
                f"BSOR file version {version} is newer than supported version {MAX_SUPPORTED_BSOR_VERSION}. "
                "Some features may not be parsed correctly or at all."
            )

        info_obj = Info.from_stream(f)

        # Helper to read lists with magic byte and count
        def _read_list_section[T](
            stream: BinaryIO, 
            expected_magic: int, 
            item_parser: Callable[[BinaryIO], T],
            section_name: str
        ) -> List[T]:
            magic_byte = decode_byte(stream)
            if magic_byte != expected_magic:
                raise BSException(f"{section_name} magic byte mismatch. Expected {expected_magic}, got {magic_byte}.")
            return make_list_from_stream(stream, decode_int, item_parser)

        frames_list = _read_list_section(f, FRAMES_MAGIC_BYTE, Frame.from_stream, "Frames")
        notes_list = _read_list_section(f, NOTES_MAGIC_BYTE, Note.from_stream, "Notes")
        walls_list = _read_list_section(f, WALLS_MAGIC_BYTE, Wall.from_stream, "Walls")
        heights_list = _read_list_section(f, HEIGHTS_MAGIC_BYTE, HeightEvent.from_stream, "Heights")
        pauses_list = _read_list_section(f, PAUSES_MAGIC_BYTE, Pause.from_stream, "Pauses")
        
        controller_offsets_obj = None
        user_data_list = []

        # Check for optional sections by trying to peek at the next byte
        # This indicates if there's more data for V2+ features
        try:
            next_section_magic_peek = f.peek(1) # type: ignore # peek returns bytes
            if not next_section_magic_peek: # EOF
                pass # No more sections
            else:
                next_section_magic = int.from_bytes(next_section_magic_peek[:1], 'little')
                
                if next_section_magic == CONTROLLER_OFFSETS_MAGIC_BYTE:
                    decode_byte(f) # Consume the peeked byte
                    controller_offsets_obj = ControllerOffsets.from_stream(f)
                    
                    # Check for UserData after ControllerOffsets
                    next_section_magic_peek = f.peek(1)
                    if not next_section_magic_peek: pass
                    else:
                        next_section_magic = int.from_bytes(next_section_magic_peek[:1], 'little')
                        if next_section_magic == USER_DATA_MAGIC_BYTE:
                            user_data_list = _read_list_section(f, USER_DATA_MAGIC_BYTE, UserDataEntry.from_stream, "UserData")

                elif next_section_magic == USER_DATA_MAGIC_BYTE: # ControllerOffsets might be absent
                     user_data_list = _read_list_section(f, USER_DATA_MAGIC_BYTE, UserDataEntry.from_stream, "UserData")

        except EOFError: # Raised by _read_bytes_safe if peek tries to read past EOF
            logging.debug("EOF reached while checking for optional BSOR sections.")
        except Exception as e: # Other errors during peek or optional section parsing
            # This could be struct.error from peek, or other issues.
            # It's safer to log and assume no more optional sections if peeking fails.
            logging.warning(f"Error while checking for optional BSOR sections: {e}. Assuming no more data.")
            # Ensure `f` is not left in a bad state if `peek` is not available or fails.
            # The original code used a try-except around peek, then read and seeked back.
            # A simpler way for robust EOF check:
            # current_pos = f.tell()
            # try:
            #   byte = decode_byte(f)
            #   f.seek(current_pos) # rewind
            #   # Now process `byte` for optional sections
            # except EOFError:
            #   pass # No more data

        return cls(
            magic_number=magic,
            file_version=version,
            info=info_obj,
            frames=frames_list,
            notes=notes_list,
            walls=walls_list,
            heights=heights_list,
            pauses=pauses_list,
            controller_offsets=controller_offsets_obj,
            user_data=user_data_list
        )

    def to_json_dict(self) -> Dict[str, Any]:
        # Pydantic's model_dump should handle most of this.
        # We need to ensure sub-models also use their to_json_dict if they have custom ones.
        # By default, Pydantic will call model_dump on nested models.
        return self.model_dump(mode='json', by_alias=True)
