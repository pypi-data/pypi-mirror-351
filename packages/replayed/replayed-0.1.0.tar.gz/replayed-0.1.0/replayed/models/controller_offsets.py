"""
replayed.models.controller_offsets
----------------------------------

Model for controller offset data, if present.
This is often part of extended BSOR features or specific game versions.
"""
from typing import BinaryIO, Optional, Dict, Any
from pydantic import Field

from ..base_types import PydanticWritableBase, BSException
from ..io_utils import decode_byte
from ..constants import CONTROLLER_OFFSETS_MAGIC_BYTE
from .common import VRObject


class ControllerOffsets(PydanticWritableBase):
    """Stores VR controller offset data."""
    left: VRObject = Field(default_factory=VRObject)
    right: VRObject = Field(default_factory=VRObject)

    def write(self, f: BinaryIO) -> None:
        # The magic byte for this section is typically written *before* calling this,
        # by the main Bsor writer, if this section exists.
        # encode_byte(f, CONTROLLER_OFFSETS_MAGIC_BYTE) # This is handled by Bsor.write
        self.left.write(f)
        self.right.write(f)

    @classmethod
    def from_stream(cls, f: BinaryIO) -> "ControllerOffsets":
        # Magic byte is read by the main Bsor parser before calling this.
        return cls(
            left=VRObject.from_stream(f),
            right=VRObject.from_stream(f)
        )

    def to_json_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode='json')