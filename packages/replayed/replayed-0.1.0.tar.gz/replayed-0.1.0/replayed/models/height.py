"""
replayed.models.height
----------------------

Model for player height change events.
"""
from typing import BinaryIO, Dict, Any
from pydantic import Field

from ..base_types import PydanticWritableBase
from ..io_utils import decode_float, encode_float

class HeightEvent(PydanticWritableBase): # Renamed from Height to avoid conflict with Info.height
    """Represents a player height change event during the replay."""
    # Field name in original struct was 'height', clashing with Info.height.
    # Using 'player_height_value' or similar for clarity if this is distinct.
    # The original `make_height` assigned to `h.height`.
    value: float = Field(default=0.0, alias="height") # The new player height value
    time: float = Field(default=0.0)   # In-game time of the height change event

    def write(self, f: BinaryIO) -> None:
        encode_float(f, self.value)
        encode_float(f, self.time)

    @classmethod
    def from_stream(cls, f: BinaryIO) -> "HeightEvent":
        return cls(
            height=decode_float(f), # Use alias for construction
            time=decode_float(f)
        )

    def to_json_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode='json', by_alias=True)