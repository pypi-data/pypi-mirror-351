"""
replayed.models.common
----------------------

Common data structures used in BSOR models.
"""
from typing import BinaryIO, Tuple, Dict, Any
from pydantic import computed_field, Field

from ..base_types import PydanticWritableBase
from ..io_utils import encode_float, decode_float

class Position(PydanticWritableBase):
    """Represents a 3D position."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def write(self, f: BinaryIO) -> None:
        encode_float(f, self.x)
        encode_float(f, self.y)
        encode_float(f, self.z)

    @classmethod
    def from_stream(cls, f: BinaryIO) -> "Position":
        return cls(
            x=decode_float(f),
            y=decode_float(f),
            z=decode_float(f)
        )

class Rotation(PydanticWritableBase):
    """Represents a 3D rotation as a quaternion."""
    x: float = Field(default=0.0, alias="x_rot")
    y: float = Field(default=0.0, alias="y_rot")
    z: float = Field(default=0.0, alias="z_rot")
    w: float = Field(default=0.0, alias="w_rot") # Identity quaternion typically (0,0,0,1)

    def write(self, f: BinaryIO) -> None:
        encode_float(f, self.x)
        encode_float(f, self.y)
        encode_float(f, self.z)
        encode_float(f, self.w)

    @classmethod
    def from_stream(cls, f: BinaryIO) -> "Rotation":
        return cls(
            x_rot=decode_float(f), # Using alias for constructor
            y_rot=decode_float(f),
            z_rot=decode_float(f),
            w_rot=decode_float(f)
        )

class VRObject(PydanticWritableBase):
    """Represents a VR tracked object with position and rotation."""
    position: Position = Field(default_factory=Position)
    rotation: Rotation = Field(default_factory=Rotation) # Quaternion: x, y, z, w

    def write(self, f: BinaryIO) -> None:
        self.position.write(f)
        self.rotation.write(f)

    @classmethod
    def from_stream(cls, f: BinaryIO) -> "VRObject":
        return cls(
            position=Position.from_stream(f),
            rotation=Rotation.from_stream(f)
        )

    def to_json_dict(self) -> Dict[str, Any]:
        """Custom JSON dictionary representation."""
        return {
            "position": self.position.model_dump(mode='json'),
            "rotation": self.rotation.model_dump(mode='json', by_alias=True) # Ensure aliases are used if defined
        }