"""
replayed.constants
------------------

Constants used throughout the replayed module.
"""
from typing import Dict

# Note Event Types
NOTE_EVENT_GOOD: int = 0
NOTE_EVENT_BAD: int = 1
NOTE_EVENT_MISS: int = 2
NOTE_EVENT_BOMB: int = 3

# Note Scoring Types
NOTE_SCORE_TYPE_NORMAL_1: int = 0
NOTE_SCORE_TYPE_IGNORE: int = 1
NOTE_SCORE_TYPE_NOSCORE: int = 2
NOTE_SCORE_TYPE_NORMAL_2: int = 3  # Often treated the same as NORMAL_1
NOTE_SCORE_TYPE_SLIDERHEAD: int = 4
NOTE_SCORE_TYPE_SLIDERTAIL: int = 5
NOTE_SCORE_TYPE_BURSTSLIDERHEAD: int = 6
NOTE_SCORE_TYPE_BURSTSLIDERELEMENT: int = 7

# Saber Types
SABER_LEFT: int = 1  # Typically blue saber
SABER_RIGHT: int = 0 # Typically red saber

# BSOR File Format Constants
MAX_SUPPORTED_BSOR_VERSION: int = 1
BSOR_MAGIC_NUMBER_HEX: str = '0x442d3d69' # "BSOR" in a specific byte order, results in 737000000 decimal
BSOR_MAGIC_NUMBER_INT: int = 737000000 # int.from_bytes(b'BSOR'[::-1], 'little') if BSOR was 'R OSB'

# Magic bytes for different sections in BSOR file
INFO_MAGIC_BYTE: int = 0
FRAMES_MAGIC_BYTE: int = 1
NOTES_MAGIC_BYTE: int = 2
WALLS_MAGIC_BYTE: int = 3
HEIGHTS_MAGIC_BYTE: int = 4
PAUSES_MAGIC_BYTE: int = 5
CONTROLLER_OFFSETS_MAGIC_BYTE: int = 6
USER_DATA_MAGIC_BYTE: int = 7


# Lookup Dictionaries
LOOKUP_DICT_SCORING_TYPE: Dict[int, str] = {
    NOTE_SCORE_TYPE_NORMAL_1: 'Normal',
    NOTE_SCORE_TYPE_IGNORE: 'Ignore',
    NOTE_SCORE_TYPE_NOSCORE: 'NoScore',
    NOTE_SCORE_TYPE_NORMAL_2: 'Normal', # Same as NORMAL_1
    NOTE_SCORE_TYPE_SLIDERHEAD: 'SliderHead',
    NOTE_SCORE_TYPE_SLIDERTAIL: 'SliderTail',
    NOTE_SCORE_TYPE_BURSTSLIDERHEAD: 'BurstSliderHead',
    NOTE_SCORE_TYPE_BURSTSLIDERELEMENT: 'BurstSliderElement'
}

LOOKUP_DICT_EVENT_TYPE: Dict[int, str] = {
    NOTE_EVENT_GOOD: 'Cut',
    NOTE_EVENT_BAD: 'BadCut',
    NOTE_EVENT_MISS: 'Miss',
    NOTE_EVENT_BOMB: 'Bomb'
}

LOOKUP_DICT_SABER_TYPE: Dict[int, str] = {
    SABER_LEFT: 'LeftSaber',
    SABER_RIGHT: 'RightSaber'
}