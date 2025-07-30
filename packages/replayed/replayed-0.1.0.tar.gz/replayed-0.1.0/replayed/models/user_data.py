"""
replayed.models.user_data
-------------------------

Model for custom user data entries in a BSOR file.
This allows mods or external tools to store arbitrary information.
"""
from typing import BinaryIO, List, Dict, Any
from pydantic import Field, computed_field

from ..base_types import PydanticWritableBase
from ..io_utils import (
    decode_string, decode_int, decode_byte, _read_bytes_safe,
    encode_string, encode_int # encode_byte is part of io_utils
)

class UserDataEntry(PydanticWritableBase): # Renamed from UserData to avoid conflict with list name
    """Represents a single key-value entry for custom user data."""
    key: str = Field(default="")
    # The original `bytes: List[bytes]` where each inner `bytes` was read after `decode_byte(f)` for its length
    # seems unusual. Typically, it would be a single byte array for the value.
    # `u.bytes = [f.read(decode_byte(f)) for _ in range(byte_count)]`
    # This means `byte_count` is the number of *chunks*, and each chunk's length is read first.
    # This is a very specific structure. Let's try to model it.
    # If it's simpler, like one byte array, the model would be `value_bytes: bytes`.
    # Given the original:
    byte_chunks: List[bytes] = Field(default_factory=list)

    def write(self, f: BinaryIO) -> None:
        encode_string(f, self.key)
        encode_int(f, len(self.byte_chunks)) # Number of chunks
        for chunk in self.byte_chunks:
            # Original `decode_byte(f)` reads a single byte for length.
            # So, length of each chunk must be <= 255.
            if len(chunk) > 255:
                raise ValueError(f"UserDataEntry chunk for key '{self.key}' is too long ({len(chunk)} bytes). Max 255 bytes per chunk for this encoding.")
            f.write(len(chunk).to_bytes(1, 'little')) # Write chunk length (1 byte)
            f.write(chunk) # Write chunk data

    @classmethod
    def from_stream(cls, f: BinaryIO) -> "UserDataEntry":
        key = decode_string(f)
        num_chunks = decode_int(f)
        chunks = []
        for _ in range(num_chunks):
            chunk_len = decode_byte(f) # Length of this specific chunk
            chunk_data = _read_bytes_safe(f, chunk_len)
            chunks.append(chunk_data)
        return cls(key=key, byte_chunks=chunks)

    @computed_field
    @property
    def combined_value_bytes(self) -> bytes:
        """Combines all byte chunks into a single bytes object."""
        return b"".join(self.byte_chunks)

    def to_json_dict(self) -> Dict[str, Any]:
        # Representing bytes in JSON usually means base64 encoding or similar.
        # For now, let's provide the key and perhaps a representation of the chunks.
        return {
            "key": self.key,
            # "byte_chunks_lengths": [len(c) for c in self.byte_chunks], # For debug
            "combined_value_base64": self.combined_value_bytes.encode('base64').decode('ascii').strip() if self.byte_chunks else ""
            # Or keep it simple:
            # "value_hex": self.combined_value_bytes.hex() if self.byte_chunks else ""
        }