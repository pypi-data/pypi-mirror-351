"""
replayed.models.pause
---------------------

Model for pause events in the replay.
"""
from typing import BinaryIO, Dict, Any
from pydantic import Field

from ..base_types import PydanticWritableBase
from ..io_utils import decode_long, decode_float, encode_long, encode_float

class Pause(PydanticWritableBase):
    """Represents a pause event during the game."""
    # Duration is often in milliseconds or a similar high-resolution unit if it's a long.
    # BSOR spec usually implies float for time, but 'long' was specified for duration.
    duration: int = Field(default=0) # Duration of the pause (e.g., in ticks or ms)
    time: float = Field(default=0.0)   # In-game time when the pause started

    def write(self, f: BinaryIO) -> None:
        encode_long(f, self.duration) # Use encode_long as specified
        encode_float(f, self.time)

    @classmethod
    def from_stream(cls, f: BinaryIO) -> "Pause":
        return cls(
            duration=decode_long(f),
            time=decode_float(f)
        )
    
    def to_json_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode='json')