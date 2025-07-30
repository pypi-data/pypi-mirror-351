"""
replayed.base_types
-------------------

Base types and custom exceptions for the replayed module.
"""
from abc import ABC, abstractmethod
from typing import BinaryIO, Any, Dict
from pydantic import BaseModel

class BSException(Exception):
    """Custom exception for Bsor parsing and processing errors."""
    pass

class Writable(ABC):
    """Abstract base class for objects that can be written to a binary stream."""
    @abstractmethod
    def write(self, f: BinaryIO) -> None:
        """Writes the object's binary representation to the file stream."""
        pass

class PydanticWritableBase(BaseModel, Writable):
    """
    Base model for Pydantic models that also need to be Writable.
    This combines Pydantic's data validation and serialization with custom binary writing.
    """
    class Config:
        arbitrary_types_allowed = True

    def write(self, f: BinaryIO) -> None:
        # Default implementation or raise NotImplementedError
        # Each subclass will need to implement this specifically.
        raise NotImplementedError(f"Write method not implemented for {self.__class__.__name__}")

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Provides a dictionary representation suitable for JSON serialization,
        attempting to match the structure of original json_dict methods.
        Override in subclasses for specific structures.
        """
        return self.model_dump(mode='json')
