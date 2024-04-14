from typing import Optional, List, Tuple, Callable, Any

import bpy
from .midi_analysis.Note import Note


class AnalyzedNote:
    def __init__(self, note: Note, use_file_tempo: bool, ms_per_tick: float, frames_per_second: float,
                 frame_offset: int, scale_factor: Optional[float], start_at_note_end: bool,
                 non_scaled_action_length: Optional[int]):
        self.note = note
        self.note_start_frame = 0
        self.note_end_frame = 0  # the last frame of the note (does not account for action scaling)
        self.note_length_frames = 0
        self.action_length_frames = 0
        self.action_start_frame = 0
        self.action_end_frame = 0  # the last frame of the action
        self.start_at_note_end = start_at_note_end
        self.non_scaled_action_length = non_scaled_action_length
        self.scale_factor = scale_factor  # if None then no scaling

        self.analyze_note(use_file_tempo, ms_per_tick, frames_per_second, frame_offset)

    def analyze_note(self, use_file_tempo: bool, ms_per_tick: float, frames_per_second: float, frame_offset: int):
        start_time_ms = self.note.start_time if use_file_tempo else self.note.start_time_ticks * ms_per_tick
        end_time_ms = self.note.end_time if use_file_tempo else self.note.end_time_ticks * ms_per_tick

        self.note_start_frame = int((start_time_ms / 1000) * frames_per_second + frame_offset)
        self.note_end_frame = int((end_time_ms / 1000) * frames_per_second + frame_offset)
        # make sure note length is at least one frame
        if self.note_end_frame <= self.note_start_frame:
            self.note_end_frame = self.note_end_frame + 1
        self.note_length_frames = self.note_end_frame - self.note_start_frame

        if self.non_scaled_action_length is None:
            self.non_scaled_action_length = self.note_length_frames

        if self.scale_factor is None:
            self.action_length_frames = self.non_scaled_action_length
        else:
            self.action_length_frames = max(self.note_length_frames * self.scale_factor, 1)

        self.action_start_frame = self.note_start_frame
        self.action_end_frame = self.note_start_frame + self.action_length_frames

        if self.start_at_note_end:
            self.action_start_frame += self.note_length_frames
            self.action_end_frame += self.note_length_frames

    def is_scaled_down(self):
        if self.non_scaled_action_length is None:
            return False
        return self.action_length_frames < self.non_scaled_action_length


class ExistingNoteOverlapsLayer:
    def __init__(self, layer, overlaps_from_layer, overlap_to_start_end_pair: Callable[[Any], Tuple[int, int]]):
        """
        :param layer: object representing the layer
        :param overlaps_from_layer: function to get list of objects representing the existing overlaps on the layer
        :param overlap_to_start_end_pair: function to get the start and end frame of the overlap from the object
        """
        self.overlap_checker = OverlapChecker(
            [overlap_to_start_end_pair(x) for x in overlaps_from_layer(layer)])
        self.existing_pairs = [overlap_to_start_end_pair(x) for x in overlaps_from_layer(layer)]

    def has_room_for_note(self, analyzed_note: AnalyzedNote, same_frame_is_overlap: bool):
        return self.overlap_checker.has_room_for_pair(
            (analyzed_note.action_start_frame, analyzed_note.action_end_frame), same_frame_is_overlap)


class NotesLayer:

    def __init__(self, existing_note_overlaps_layer: Optional[ExistingNoteOverlapsLayer], same_frame_is_overlap: bool,
                 frame_length_for_overlap: Optional[int] = None):
        self.notes = []
        self.last_note_added = None
        self.existing_note_overlaps_layer = existing_note_overlaps_layer
        self.same_frame_is_overlap = same_frame_is_overlap
        self.frame_length_for_overlap = frame_length_for_overlap

    def add_note(self, analyzed_note: AnalyzedNote):
        self.notes.append(analyzed_note)
        self.last_note_added = analyzed_note

    def has_room_for_note(self, analyzed_note: AnalyzedNote):
        return not self.overlaps_last_note(analyzed_note) and not self.overlaps_existing(analyzed_note)

    def overlaps_existing(self, analyzed_note: AnalyzedNote):
        return self.existing_note_overlaps_layer is not None and \
            not self.existing_note_overlaps_layer.has_room_for_note(analyzed_note, self.same_frame_is_overlap)

    def overlaps_last_note(self, analyzed_note: AnalyzedNote) -> bool:
        if self.last_note_added is None:
            return False
        else:
            end_frame = self.last_note_added.action_end_frame if self.frame_length_for_overlap is None else \
                self.last_note_added.action_start_frame + self.frame_length_for_overlap
            if self.same_frame_is_overlap:
                return analyzed_note.action_start_frame <= end_frame and \
                    end_frame >= self.last_note_added.action_start_frame
            else:
                return analyzed_note.action_start_frame < end_frame and \
                    end_frame > self.last_note_added.action_start_frame


class OverlapChecker:
    def __init__(self, start_end_pairs: List[Tuple[int, int]]):
        self.start_end_paris = start_end_pairs
        self.current_pair_index = 0
        self.current_pair = None

    def has_room_for_pair(self, start_end_pair: Tuple[int, int], same_frame_is_overlap: bool):
        """
        Checks if start_end_pair would fit without overlap. Checks to this method need to be called in sorted order.
        :param start_end_pair: (frame start, frame end)
        :param same_frame_is_overlap: (x, y) overlaps (y, z) if True.
        :return: True if start_end_pair would fit without overlap
        """
        if self.current_pair_index < len(self.start_end_paris):
            self.current_pair = self.start_end_paris[self.current_pair_index]

            while self.current_pair is not None and \
                    ((same_frame_is_overlap and self.current_pair[1] < start_end_pair[0]) or
                     (not same_frame_is_overlap and self.current_pair[1] <= start_end_pair[0])):
                self.current_pair_index = self.current_pair_index + 1
                self.current_pair = self.start_end_paris[self.current_pair_index] if \
                    self.current_pair_index < len(self.start_end_paris) else None

        return not self.overlaps_last_pair(start_end_pair, same_frame_is_overlap)

    def overlaps_last_pair(self, start_end_pair, same_frame_is_overlap: bool) -> bool:
        if self.current_pair is None:
            return False
        elif same_frame_is_overlap:
            return start_end_pair[0] <= self.current_pair[1] and \
                start_end_pair[1] >= self.current_pair[0]
        else:
            return start_end_pair[0] < self.current_pair[1] and \
                start_end_pair[1] > self.current_pair[0]

    def reset_index(self):
        """
        Reset overlap checking back to the first start end pair.
        """
        self.current_pair_index = 0
