"""
replayed.models.frame
---------------------

Model for tracking frames in a BSOR replay.
"""
from typing import BinaryIO, List, Dict, Any
from pydantic import Field

from ..base_types import PydanticWritableBase
from ..io_utils import decode_float, decode_int, encode_float, encode_int
from .common import VRObject

class Frame(PydanticWritableBase):
    """Represents a single frame of tracking data."""
    time: float = Field(default=0.0) # In-game time of this frame
    fps: int = Field(default=0)      # Frames Per Second at the time of this frame (often reported as 0 if not available)
    head: VRObject = Field(default_factory=VRObject)
    left_hand: VRObject = Field(default_factory=VRObject, alias="leftHand")
    right_hand: VRObject = Field(default_factory=VRObject, alias="rightHand")

    def write(self, f: BinaryIO) -> None:
        encode_float(f, self.time)
        encode_int(f, self.fps)
        self.head.write(f)
        self.left_hand.write(f)
        self.right_hand.write(f)

    @classmethod
    def from_stream(cls, f: BinaryIO) -> "Frame":
        return cls(
            time=decode_float(f),
            fps=decode_int(f),
            head=VRObject.from_stream(f),
            leftHand=VRObject.from_stream(f), # Use alias
            rightHand=VRObject.from_stream(f)  # Use alias
        )

    def to_json_dict(self) -> Dict[str, Any]:
        # Pydantic's model_dump with by_alias=True should handle this.
        # VRObject has its own to_json_dict which will be called.
        return self.model_dump(mode='json', by_alias=True)