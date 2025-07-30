"""
replayed.models.info
--------------------

Model for the replay's metadata (Info section).
"""
from typing import BinaryIO, Dict, Any
from pydantic import Field

from ..base_types import PydanticWritableBase, BSException
from ..io_utils import (
    decode_byte, decode_string, decode_string_maybe_utf16, decode_int,
    decode_float, decode_bool,
    encode_byte, encode_string, encode_int, encode_float, encode_bool,
    write_list_polymorphic
)
from ..constants import INFO_MAGIC_BYTE

class Info(PydanticWritableBase):
    """Contains metadata about the replay and the game session."""
    # File and game versioning
    version: str = Field(default="") # BSOR file format version string
    game_version: str = Field(default="", alias="gameVersion")
    timestamp: str = Field(default="") # ISO 8601 or similar timestamp string

    # Player identification
    player_id: str = Field(default="", alias="playerId")
    player_name: str = Field(default="", alias="playerName") # Potentially needs special UTF-16 handling
    platform: str = Field(default="") # e.g., "STEAM", "OCULUS"

    # Tracking and hardware
    tracking_system: str = Field(default="", alias="trackingSystem") # e.g., "OpenVR"
    hmd: str = Field(default="", alias="hmd") # Head-Mounted Display name
    controller: str = Field(default="") # Controller type

    # Song details
    song_hash: str = Field(default="", alias="songHash") # Beatmap hash (usually SHA1)
    song_name: str = Field(default="", alias="songName") # Song title
    mapper: str = Field(default="") # Map author
    difficulty: str = Field(default="") # e.g., "ExpertPlus"

    # Score and gameplay mode
    score: int = Field(default=0)
    mode: str = Field(default="") # Game mode, e.g., "Standard", "OneSaber"
    environment: str = Field(default="") # Name of the game environment
    modifiers: str = Field(default="") # Comma-separated list of active modifiers (e.g., "FS,NA")
    jump_distance: float = Field(default=0.0, alias="jumpDistance") # Note jump distance/speed setting
    left_handed: bool = Field(default=False, alias="leftHanded")
    height: float = Field(default=0.0) # Player height setting

    # Performance timing
    start_time: float = Field(default=0.0, alias="startTime") # In-game time when recording started (often 0)
    fail_time: float = Field(default=0.0, alias="failTime") # In-game time of fail, 0 if no fail
    speed: float = Field(default=0.0) # Song speed multiplier (e.g., 1.0 for normal, 1.5 for 150%)

    def write(self, f: BinaryIO) -> None:
        encode_byte(f, INFO_MAGIC_BYTE) # Magic byte for Info section
        
        # The original `write_things` was a generic helper.
        # Here, we explicitly write each field according to its type.
        # This list matches the order in the original `make_info` reading.
        fields_to_write = [
            self.version, self.game_version, self.timestamp,
            self.player_id, self.player_name, self.platform,
            self.tracking_system, self.hmd, self.controller,
            self.song_hash, self.song_name, self.mapper, self.difficulty,
            self.score, self.mode, self.environment, self.modifiers,
            self.jump_distance, self.left_handed, self.height,
            self.start_time, self.fail_time, self.speed
        ]
        
        # This is not how write_list_polymorphic is designed to be used.
        # It expects a list of items, not a list of attributes of a single item.
        # We need to call the specific encode functions for each attribute.
        
        encode_string(f, self.version)
        encode_string(f, self.game_version)
        encode_string(f, self.timestamp)
        encode_string(f, self.player_id)
        encode_string(f, self.player_name) # Assuming standard UTF-8 encoding for writing.
                                         # If it needs to be maybe_utf16 for writing, that's complex.
                                         # The format typically uses standard UTF-8 for writing.
        encode_string(f, self.platform)
        encode_string(f, self.tracking_system)
        encode_string(f, self.hmd)
        encode_string(f, self.controller)
        encode_string(f, self.song_hash)
        encode_string(f, self.song_name)
        encode_string(f, self.mapper)
        encode_string(f, self.difficulty)
        encode_int(f, self.score)
        encode_string(f, self.mode)
        encode_string(f, self.environment)
        encode_string(f, self.modifiers)
        encode_float(f, self.jump_distance)
        encode_bool(f, self.left_handed)
        encode_float(f, self.height)
        encode_float(f, self.start_time)
        encode_float(f, self.fail_time)
        encode_float(f, self.speed)


    @classmethod
    def from_stream(cls, f: BinaryIO) -> "Info":
        info_start_byte = decode_byte(f)
        if info_start_byte != INFO_MAGIC_BYTE:
            raise BSException(f"Info magic byte mismatch. Expected {INFO_MAGIC_BYTE}, got {info_start_byte}.")

        return cls(
            version=decode_string(f),
            gameVersion=decode_string(f),
            timestamp=decode_string(f),
            playerId=decode_string(f),
            playerName=decode_string_maybe_utf16(f), # Special handling for this field
            platform=decode_string(f),
            trackingSystem=decode_string(f),
            hmd=decode_string(f),
            controller=decode_string(f),
            songHash=decode_string(f),
            songName=decode_string_maybe_utf16(f), # Special handling
            mapper=decode_string_maybe_utf16(f),   # Special handling
            difficulty=decode_string(f),
            score=decode_int(f),
            mode=decode_string(f),
            environment=decode_string(f),
            modifiers=decode_string(f),
            jumpDistance=decode_float(f),
            leftHanded=decode_bool(f),
            height=decode_float(f),
            startTime=decode_float(f),
            failTime=decode_float(f),
            speed=decode_float(f)
        )

    def to_json_dict(self) -> Dict[str, Any]:
        # Pydantic's model_dump with by_alias=True should handle this.
        return self.model_dump(mode='json', by_alias=True)
