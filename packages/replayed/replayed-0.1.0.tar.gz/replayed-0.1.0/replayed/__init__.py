"""
replayed - A Python library for parsing and analyzing Beat Saber BSOR replay files.
"""
__version__ = "0.1.0"

from .base_types import BSException
from .models import (
    Bsor, Info, Frame, Note, Wall, HeightEvent, Pause, ControllerOffsets, UserDataEntry,
    Cut, VRObject, Position, Rotation,
    NoteIDData, NoteCutInfo
)
from .io_utils import (
    decode_int, decode_long, decode_byte, decode_bool, decode_string,
    decode_string_maybe_utf16, decode_float,
    encode_int, encode_long, encode_byte, encode_bool, encode_string, encode_float
)
from .constants import * # Export all constants

# Primary public interface
parse_bsor_from_file = Bsor.from_stream # Alias for convenience

def load_replay(file_path: str) -> Bsor:
    """Loads a BSOR replay from a file path."""
    with open(file_path, 'rb') as f:
        return Bsor.from_stream(f)

def save_replay(bsor_data: Bsor, file_path: str) -> None:
    """Saves BSOR data to a file."""
    with open(file_path, 'wb') as f:
        bsor_data.write(f)


__all__ = [
    "BSException",
    # Models
    "Bsor", "Info", "Frame", "Note", "Wall", "HeightEvent", "Pause", 
    "ControllerOffsets", "UserDataEntry", "Cut", "VRObject", "Position", "Rotation",
    "NoteIDData", "NoteCutInfo",
    # I/O (selected high-level)
    "load_replay", "save_replay", "parse_bsor_from_file",
]

# To make all constants available via replayed.SOMETHING:
# This is a bit of a wildcard import into the namespace for __all__
# A more explicit approach would be to list them.
# For now, this makes them accessible.
# If you `import replayed`, you can do `replayed.NOTE_EVENT_GOOD`.
# If you `from replayed import *`, they will be imported.
# This reflects the `from .constants import *` behavior.
