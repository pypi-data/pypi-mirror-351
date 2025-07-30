"""
replayed.models.wall
--------------------

Model for wall obstacle events.
"""
from typing import BinaryIO, Dict, Any
from pydantic import Field

from ..base_types import PydanticWritableBase
from ..io_utils import decode_int, decode_float, encode_int, encode_float

class Wall(PydanticWritableBase):
    """Represents a wall event (obstacle hit)."""
    # The original format had 'id', but this seems to be 'wallId' in some contexts
    # or just an index. For BSOR, it's often just called 'noteID' or similar for walls too.
    # Let's stick to 'id' if that's what the original parsing implies.
    # If it's from `decode_int(f)`, it's likely a generic ID.
    wall_id: int = Field(default=0, alias="id") # Identifier for the wall, if available
    
    # 'energy' was in original, but standard BSOR walls don't typically have 'energy'.
    # This might be from a modded format or an older version.
    # Standard wall events usually only have time.
    # For now, including it as per original structure. If it's always 0 or unused, can be removed.
    energy: float = Field(default=0.0) # Unclear what this represents for walls in standard BSOR.
                                      # Could be related to energy lost if it's a fail condition.
    
    time: float = Field(default=0.0)       # In-game time of the wall event (collision)
    
    # 'spawnTime' was also in original. Walls do have a spawn time.
    spawn_time: float = Field(default=0.0, alias="spawnTime") # Time the wall was spawned

    def write(self, f: BinaryIO) -> None:
        encode_int(f, self.wall_id)
        encode_float(f, self.energy) # If this field is kept
        encode_float(f, self.time)
        encode_float(f, self.spawn_time)

    @classmethod
    def from_stream(cls, f: BinaryIO) -> "Wall":
        return cls(
            id=decode_int(f),
            energy=decode_float(f), # If this field is kept
            time=decode_float(f),
            spawnTime=decode_float(f)
        )

    def to_json_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode='json', by_alias=True)