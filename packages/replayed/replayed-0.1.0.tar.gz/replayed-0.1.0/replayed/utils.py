"""
replayed.utils
--------------

General utility functions.
"""
import math
from typing import TypeVar, List, Any, Callable, BinaryIO

T = TypeVar('T')

def clamp(value: T, min_value: T, max_value: T) -> T:
    """Clamps a value between a minimum and maximum."""
    return max(min_value, min(value, max_value))

def round_half_up(n: float) -> int:
    """Rounds a float to the nearest int, with .5 rounding up."""
    return math.floor(n + 0.5)

def make_list_from_stream(f: BinaryIO, count_decoder: Callable[[BinaryIO], int], item_decoder: Callable[[BinaryIO], T]) -> List[T]:
    """
    Reads a list of items from a binary stream.
    The stream is expected to first contain the count of items, then the items themselves.

    Args:
        f: The binary stream to read from.
        count_decoder: A function that decodes the number of items from the stream.
        item_decoder: A function that decodes a single item from the stream.

    Returns:
        A list of decoded items.
    """
    count = count_decoder(f)
    return [item_decoder(f) for _ in range(count)]
