from typing import List, Optional, Iterator
from .midi_analysis.Note import Note
from .midi_data import LoadedMidiData


class AnalyzedNote:
    def __init__(self, note: Note, use_file_tempo: bool, ms_per_tick: float, frames_per_second: float,
                 frame_offset: int, note_scale_factor: Optional[float], start_at_note_end: bool,
                 non_scaled_action_length: Optional[int]):
        self.note = note
        self.start_frame: int = 0
        self.end_frame: int = 0  # the last frame of the note (does not account for action scaling)
        self.note_length_frames: int = 0
        self.action_length_frames: int = 0
        self.action_start_frame = 0
        self.action_end_frame = 0  # the last frame of the action
        self.start_at_note_end = start_at_note_end
        self.non_scaled_action_length = non_scaled_action_length
        self.note_scale_factor = note_scale_factor

        self.analyze_note(use_file_tempo, ms_per_tick, frames_per_second, frame_offset)

    def analyze_note(self, use_file_tempo: bool, ms_per_tick: float, frames_per_second: float, frame_offset: int):
        start_time_ms = self.note.startTime if use_file_tempo else self.note.startTimeTicks * ms_per_tick
        end_time_ms = self.note.endTime if use_file_tempo else self.note.endTimeTicks * ms_per_tick

        self.start_frame = int((start_time_ms / 1000) * frames_per_second + frame_offset)
        self.end_frame = int((end_time_ms / 1000) * frames_per_second + frame_offset)

        # make sure note length is at least one frame
        if self.end_frame <= self.start_frame:
            self.end_frame = self.end_frame + 1
        self.note_length_frames = self.start_frame - self.end_frame

        if self.non_scaled_action_length is None:
            self.non_scaled_action_length = self.note_length_frames

        if self.note_scale_factor is None:
            self.action_length_frames = self.non_scaled_action_length
        else:
            self.action_length_frames = max(self.note_length_frames * self.note_scale_factor, 1)

        self.action_start_frame = self.start_frame
        self.action_end_frame = self.start_frame + self.action_length_frames

        if self.start_at_note_end:
            self.action_start_frame += self.note_length_frames
            self.action_end_frame += self.note_length_frames


class NotesLayer:

    def __init__(self):
        self.notes: List[AnalyzedNote] = []
        self.last_note_added: Optional[AnalyzedNote] = None

    def add_note(self, analyzed_note: AnalyzedNote):
        self.notes.append(analyzed_note)
        self.last_note_added = analyzed_note

    def has_room_for_note(self, analyzed_note: AnalyzedNote):
        return not self.overlaps_last_note(analyzed_note)

    def overlaps_last_note(self, analyzed_note: AnalyzedNote) -> bool:
        if self.last_note_added is None:
            return False
        else:
            return analyzed_note.action_start_frame < self.last_note_added.action_end_frame and \
                   analyzed_note.action_end_frame > self.last_note_added.action_start_frame


class NoteCollection:

    def __init__(self, notes: List[Note], loaded_midi_data: LoadedMidiData, frames_per_second: float,
                 frame_offset: int, start_at_note_end: bool, note_scale_factor: Optional[float],
                 non_scaled_action_length: Optional[int]):

        self.layers: List[NotesLayer] = []  # overlap check starting at bottom layer working up
        self.layers_top_down_overlap: List[NotesLayer] = []  # overlap check starting at top layer working down
        self.all_notes: List[AnalyzedNote] = []
        self.frames_per_second = frames_per_second
        self.frame_offset = frame_offset
        self.note_scale_factor = note_scale_factor
        self.start_at_note_end = start_at_note_end
        self.raw_notes = notes
        self.loaded_midi_data = loaded_midi_data
        self.non_scaled_action_length = non_scaled_action_length

        self.calculate_notes()

    def calculate_notes(self):
        for note in self.raw_notes:
            analyzed_note = self.create_analyzed_note(note=note, use_file_tempo=self.loaded_midi_data.use_file_tempo,
                                                      ms_per_tick=self.loaded_midi_data.ms_per_tick,
                                                      frames_per_second=self.frames_per_second,
                                                      frame_offset=self.frame_offset,
                                                      note_scale_factor=self.note_scale_factor,
                                                      start_at_note_end=self.start_at_note_end,
                                                      non_scaled_action_length=self.non_scaled_action_length)
            self.add_note_to_layer(analyzed_note, self.layers, False)
            self.add_note_to_layer(analyzed_note, self.layers_top_down_overlap, True,
                                   reversed(self.layers_top_down_overlap))
            self.all_notes.append(analyzed_note)

    def add_note_to_layer(self, analyzed_note: AnalyzedNote, layers: List[NotesLayer], last_track_with_room: bool,
                          iterator: Optional[Iterator[NotesLayer]] = None):
        if iterator is None:
            iterator = layers

        if last_track_with_room:
            layer_to_add = None
            for layer in iterator:
                if layer.has_room_for_note(analyzed_note):
                    layer_to_add = layer
                else:
                    break
            if layer_to_add is not None:
                layer_to_add.add_note(analyzed_note)
                return
        else:
            for layer in iterator:
                if layer.has_room_for_note(analyzed_note):
                    layer.add_note(analyzed_note)
                    return

        note_added = False
        while not note_added:
            new_layer = self.create_new_layer(layers)
            if new_layer.has_room_for_note(analyzed_note):
                new_layer.add_note(analyzed_note)
                note_added = True

    def create_new_layer(self, layers):
        new_layer = self.create_notes_layer()
        layers.append(new_layer)
        return new_layer

    def create_notes_layer(self):
        return NotesLayer()

    def create_analyzed_note(self, note: Note, use_file_tempo: bool, ms_per_tick: float, frames_per_second: float,
                             frame_offset: int, note_scale_factor: float, start_at_note_end: bool,
                             non_scaled_action_length: Optional[int]) -> AnalyzedNote:
        return AnalyzedNote(note=note, use_file_tempo=use_file_tempo,
                            ms_per_tick=ms_per_tick,
                            frames_per_second=frames_per_second,
                            frame_offset=frame_offset,
                            note_scale_factor=note_scale_factor,
                            start_at_note_end=start_at_note_end,
                            non_scaled_action_length=non_scaled_action_length)
