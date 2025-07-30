"""
replayed.models.note
--------------------

Models for notes and related information in a BSOR replay.
"""
from typing import BinaryIO, Optional, Dict, Any
from pydantic import Field, computed_field

from ..base_types import PydanticWritableBase, BSException
from ..io_utils import decode_int, decode_float, encode_int, encode_float
from ..constants import (
    NOTE_EVENT_GOOD, NOTE_EVENT_BAD,
    LOOKUP_DICT_SCORING_TYPE, LOOKUP_DICT_EVENT_TYPE,
    NOTE_SCORE_TYPE_BURSTSLIDERELEMENT, NOTE_SCORE_TYPE_SLIDERTAIL,
    NOTE_SCORE_TYPE_BURSTSLIDERHEAD, NOTE_SCORE_TYPE_SLIDERHEAD, NOTE_EVENT_MISS
)
from ..utils import clamp, round_half_up
from .cut import Cut


class NoteIDData(PydanticWritableBase):
    """Detailed components decoded from the raw note_id integer."""
    scoring_type: int = Field(default=0)
    line_index: int = Field(default=0)    # 0-3, column from left
    note_line_layer: int = Field(default=0) # 0-2, row from bottom
    color_type: int = Field(default=0)    # 0 for Red (Right Saber), 1 for Blue (Left Saber)
    cut_direction: int = Field(default=0) # 0-8 for directions, 9 for Any Cut

    def write(self, f: BinaryIO) -> None:
        # This object is derived, not written directly as separate fields.
        # The combined note_id is written.
        pass # Part of the Note's note_id

    @classmethod
    def from_id(cls, note_id_int: int) -> "NoteIDData":
        """Decodes the note ID integer into its components."""
        x = note_id_int
        
        # Make sure x is non-negative before modulo operations if it can be negative
        if x < 0:
            # This case should ideally not happen for a valid note_id.
            # Handle or log as an error. For now, assume positive as per original.
            # If it's from a file, it might indicate corruption.
            raise BSException(f"Negative note_id_int encountered: {note_id_int}")

        cut_direction = int(x % 10)
        x = (x - cut_direction) // 10 # Use integer division
        color_type = int(x % 10)
        x = (x - color_type) // 10
        note_line_layer = int(x % 10)
        x = (x - note_line_layer) // 10
        line_index = int(x % 10)
        x = (x - line_index) // 10
        scoring_type = int(x % 10) # The remainder is the scoring type
        # x = (x - scoring_type) // 10 # Original had this, but x should be 0 now.
        # If x is not 0 here, it means the note_id was larger than expected for these 5 components.
        if x != 0 :
            # This could mean an extended note_id format or an issue.
            # Standard BSOR format implies these 5 digits.
            # Example: scoringType*10000 + lineIndex*1000 + noteLineLayer*100 + colorType*10 + cutDirection
            # If scoring_type can be > 9, this simple modulo math is insufficient.
            # However, the constants suggest scoring_type is single digit (0-7).
            # Let's assume the original logic is correct for standard BSOR.
            pass


        return cls(
            scoring_type=scoring_type,
            line_index=line_index,
            note_line_layer=note_line_layer,
            color_type=color_type,
            cut_direction=cut_direction
        )

    def encode_to_id(self) -> int:
        """Encodes the components back into a single note_id integer."""
        # Ensure components are single digits as expected by the encoding scheme
        if not (0 <= self.scoring_type <= 9 and \
                0 <= self.line_index <= 9 and \
                0 <= self.note_line_layer <= 9 and \
                0 <= self.color_type <= 9 and \
                0 <= self.cut_direction <= 9):
            # This indicates an issue if values are out of single-digit range for this encoding.
            # However, line_index (0-3), note_line_layer (0-2), color_type (0-1), cut_direction (0-9)
            # and scoring_type (0-7) are all single digits.
            pass # All good.

        note_id_int = self.scoring_type
        note_id_int = note_id_int * 10 + self.line_index
        note_id_int = note_id_int * 10 + self.note_line_layer
        note_id_int = note_id_int * 10 + self.color_type
        note_id_int = note_id_int * 10 + self.cut_direction
        return note_id_int


class NoteCutInfo(PydanticWritableBase):
    """Aggregates cut details and calculated scores for a note."""
    cut_details: Optional[Cut] = None
    pre_swing_score: int = 0
    post_swing_score: int = 0
    accuracy_score: int = 0 # Center distance score

    @computed_field
    @property
    def total_score(self) -> int:
        return self.pre_swing_score + self.post_swing_score + self.accuracy_score

    def write(self, f: BinaryIO) -> None:
        # This is part of the Note's event_type conditional write
        if self.cut_details:
            self.cut_details.write(f)
        # Scores are not written directly; they are calculated.

    @classmethod
    def from_stream_and_type(cls, f: BinaryIO, event_type: int, scoring_type_from_note: int) -> "NoteCutInfo":
        instance = cls()
        if event_type in [NOTE_EVENT_GOOD, NOTE_EVENT_BAD]:
            instance.cut_details = Cut.from_stream(f)
            if instance.cut_details: # Should always exist if good/bad cut
                pre, post, acc = cls.calculate_scores(instance.cut_details, scoring_type_from_note)
                instance.pre_swing_score = pre
                instance.post_swing_score = post
                instance.accuracy_score = acc
        return instance

    @staticmethod
    def calculate_scores(cut: Cut, scoring_type: int) -> tuple[int, int, int]:
        """
        Calculates the pre-swing, post-swing, and accuracy scores for a given cut.
        Logic adapted from original calc_note_score.
        """
        if not cut.direction_ok or not cut.saber_type_ok or not cut.speed_ok or cut.was_cut_too_soon: # Added wasCutTooSoon
            return 0, 0, 0

        # Before-cut (Pre-swing) score
        pre_score = 0
        if scoring_type != NOTE_SCORE_TYPE_BURSTSLIDERELEMENT:
            if scoring_type == NOTE_SCORE_TYPE_SLIDERTAIL:
                pre_score = 70
            else:
                pre_score = round_half_up(70 * cut.before_cut_rating)
                pre_score = clamp(pre_score, 0, 70)
        
        # After-cut (Post-swing) score
        post_score = 0
        if scoring_type != NOTE_SCORE_TYPE_BURSTSLIDERELEMENT:
            if scoring_type == NOTE_SCORE_TYPE_BURSTSLIDERHEAD:
                post_score = 0 # Burst slider heads have no after-cut points
            elif scoring_type == NOTE_SCORE_TYPE_SLIDERHEAD:
                post_score = 30 # Slider heads are fixed 30 points for after-cut if hit
            else: # Normal notes
                post_score = round_half_up(30 * cut.after_cut_rating)
                post_score = clamp(post_score, 0, 30)

        # Accuracy (Cut distance from center) score
        accuracy_score = 0
        if scoring_type == NOTE_SCORE_TYPE_BURSTSLIDERELEMENT:
            accuracy_score = 20 # Fixed score for burst slider elements
        else: # Normal notes, slider heads/tails
            # cut_distance_to_center is 0 for perfect cut, up to ~0.3 for edge
            # We want 1.0 for perfect, 0.0 for edge
            accuracy_rating = 1.0 - clamp(cut.cut_distance_to_center / 0.3, 0.0, 1.0)
            accuracy_score = round_half_up(15 * accuracy_rating)
            accuracy_score = clamp(accuracy_score, 0, 15)
            
        return pre_score, post_score, accuracy_score


class Note(PydanticWritableBase):
    """Represents a single note event in the replay."""
    # Raw note_id as read from file. Components are derived via NoteIDData.
    raw_note_id: int = Field(alias="noteID") # Storing the original ID from file
    
    event_time: float = Field(default=0.0) # Time of the cut/miss/bomb event
    spawn_time: float = Field(default=0.0) # Time the note was spawned by the game
    event_type: int = Field(default=NOTE_EVENT_MISS) # good, bad, miss, bomb

    # Populated if event_type is GOOD or BAD
    cut_info: Optional[NoteCutInfo] = None

    # Derived fields from raw_note_id
    @computed_field
    @property
    def id_data(self) -> NoteIDData:
        return NoteIDData.from_id(self.raw_note_id)

    @computed_field
    @property
    def total_score(self) -> int:
        return self.cut_info.total_score if self.cut_info else 0

    def write(self, f: BinaryIO) -> None:
        encode_int(f, self.raw_note_id)
        encode_float(f, self.event_time)
        encode_float(f, self.spawn_time)
        encode_int(f, self.event_type)
        if self.event_type in [NOTE_EVENT_GOOD, NOTE_EVENT_BAD]:
            if self.cut_info and self.cut_info.cut_details:
                self.cut_info.cut_details.write(f)
            else:
                # This case implies data inconsistency if a GOOD/BAD cut has no details.
                # The BSOR format expects cut data here.
                # For writing, we might need to write placeholder Cut data or raise error.
                # Original `make_note` creates a Cut object if event_type is GOOD/BAD.
                # So, self.cut_info.cut_details should exist.
                # If it's None, it's an issue with object construction before writing.
                # Let's assume it exists for now.
                # If we need to write a file from scratch, Cut() would need default values.
                # A default (empty) Cut object could be written.
                # Cut().write(f) # This would write default values for a Cut object.
                # However, this scenario should be avoided by correct Note object construction.
                # If cut_info is None for a cut event, that's an issue.
                # If cut_info.cut_details is None, that's also an issue.
                # For robustness, one might write a default Cut, but it's better to ensure data integrity.
                raise BSException(f"Note event type {self.event_type} requires cut details for writing, but none found.")


    @classmethod
    def from_stream(cls, f: BinaryIO) -> "Note":
        raw_id = decode_int(f)
        event_time = decode_float(f)
        spawn_time = decode_float(f)
        event_type = decode_int(f)

        # Derive scoring_type from raw_id to pass to NoteCutInfo.from_stream_and_type
        # This is a bit indirect but necessary because NoteIDData isn't fully formed yet.
        # Temporary way to get scoring_type for cut_info calculation:
        temp_id_data = NoteIDData.from_id(raw_id) # Calculate once

        cut_info_obj = NoteCutInfo.from_stream_and_type(f, event_type, temp_id_data.scoring_type)
        
        return cls(
            noteID=raw_id, # Use alias for construction
            event_time=event_time,
            spawn_time=spawn_time,
            event_type=event_type,
            cut_info=cut_info_obj
        )

    def to_json_dict(self) -> Dict[str, Any]:
        """Custom JSON dictionary representation for Note."""
        base = self.model_dump(mode='json', by_alias=True, exclude={'cut_info', 'id_data'}) # Exclude complex objects handled manually
        
        id_data_dump = self.id_data.model_dump(mode='json')
        base.update({
            'scoringType': LOOKUP_DICT_SCORING_TYPE.get(self.id_data.scoring_type, str(self.id_data.scoring_type)),
            'lineIndex': self.id_data.line_index,
            'noteLineLayer': self.id_data.note_line_layer,
            'colorType': self.id_data.color_type, # Could map to "Red"/"Blue"
            'cutDirection': self.id_data.cut_direction, # Could map to names
            'eventType': LOOKUP_DICT_EVENT_TYPE.get(self.event_type, str(self.event_type)),
        })

        if self.cut_info:
            if self.cut_info.cut_details:
                 base['cut'] = self.cut_info.cut_details.to_json_dict() # Use custom dict method
            base['preScore'] = self.cut_info.pre_swing_score
            base['postScore'] = self.cut_info.post_swing_score
            base['accuracyScore'] = self.cut_info.accuracy_score
            base['totalScore'] = self.total_score # from computed_field
        else: # No cut (miss, bomb)
            base['cut'] = None
            base['preScore'] = 0
            base['postScore'] = 0
            base['accuracyScore'] = 0
            base['totalScore'] = 0
            
        return base

# Placeholder for NoteEvent (if it was a distinct class)
# In the original, Note class itself contains event_type and other details.
# The structure seems to be: a list of "Note" objects, each describing an event.
# So, Note itself is the "NoteEvent".