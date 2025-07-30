"""
replayed.models.cut
-------------------

Model for note cut information.
"""
from typing import BinaryIO, List, Dict, Any
from pydantic import Field

from ..base_types import PydanticWritableBase
from ..io_utils import (
    encode_bool, decode_bool,
    encode_float, decode_float,
    encode_int, decode_int
)
from ..constants import LOOKUP_DICT_SABER_TYPE, SABER_LEFT
from .common import Position # For cutPoint, cutNormal if they become Position objects

class Cut(PydanticWritableBase):
    """Detailed information about a note cut."""
    speed_ok: bool = Field(default=False, alias="speedOK")
    direction_ok: bool = Field(default=False, alias="directionOk")
    saber_type_ok: bool = Field(default=False, alias="saberTypeOk")
    was_cut_too_soon: bool = Field(default=False)
    saber_speed: float = Field(default=0.0)
    saber_direction: Position = Field(default_factory=Position) # x, y, z
    saber_type: int = Field(default=SABER_LEFT) # SABER_LEFT or SABER_RIGHT
    time_deviation: float = Field(default=0.0)
    cut_deviation: float = Field(default=0.0) # Angle deviation from target cut plane
    cut_point: Position = Field(default_factory=Position) # x, y, z
    cut_normal: Position = Field(default_factory=Position) # x, y, z (normal vector of the cut plane)
    cut_distance_to_center: float = Field(default=0.0)
    cut_angle: float = Field(default=0.0) # Not standard BSOR, might be from a mod or older version
    before_cut_rating: float = Field(default=0.0)
    after_cut_rating: float = Field(default=0.0)

    def write(self, f: BinaryIO) -> None:
        encode_bool(f, self.speed_ok)
        encode_bool(f, self.direction_ok)
        encode_bool(f, self.saber_type_ok)
        encode_bool(f, self.was_cut_too_soon)
        encode_float(f, self.saber_speed)
        self.saber_direction.write(f)
        encode_int(f, self.saber_type)
        encode_float(f, self.time_deviation)
        encode_float(f, self.cut_deviation)
        self.cut_point.write(f)
        self.cut_normal.write(f)
        encode_float(f, self.cut_distance_to_center)
        encode_float(f, self.cut_angle)
        encode_float(f, self.before_cut_rating)
        encode_float(f, self.after_cut_rating)

    @classmethod
    def from_stream(cls, f: BinaryIO) -> "Cut":
        return cls(
            speedOK=decode_bool(f),
            directionOk=decode_bool(f),
            saberTypeOk=decode_bool(f),
            was_cut_too_soon=decode_bool(f),
            saber_speed=decode_float(f),
            saber_direction=Position.from_stream(f),
            saber_type=decode_int(f),
            time_deviation=decode_float(f),
            cut_deviation=decode_float(f),
            cut_point=Position.from_stream(f),
            cut_normal=Position.from_stream(f),
            cut_distance_to_center=decode_float(f),
            cut_angle=decode_float(f),
            before_cut_rating=decode_float(f),
            after_cut_rating=decode_float(f)
        )

    def to_json_dict(self) -> Dict[str, Any]:
        """Custom JSON dictionary representation for Cut."""
        # Pydantic's model_dump should handle aliases correctly.
        # We need to customize saber_type representation.
        dump = self.model_dump(mode='json', by_alias=True)
        dump['saberType'] = LOOKUP_DICT_SABER_TYPE.get(self.saber_type, str(self.saber_type))
        # saber_direction, cut_point, cut_normal are already Position objects which have their own model_dump
        return dump