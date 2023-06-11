if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
else:
    from . import midi_data
    from . import NoteFilterImplementations

import bpy
from typing import List, Optional, Iterator, Generator, Any, Callable, Tuple, Iterable
from .midi_data import LoadedMidiData
from .midi_analysis.Note import Note


class AnalyzedNote:
    def __init__(self, note: Note, use_file_tempo: bool, ms_per_tick: float, frames_per_second: float,
                 frame_offset: int, scale_factor: Optional[float], start_at_note_end: bool,
                 non_scaled_action_length: Optional[int]):
        self.note = note
        self.note_start_frame: int = 0
        self.note_end_frame: int = 0  # the last frame of the note (does not account for action scaling)
        self.note_length_frames: int = 0
        self.action_length_frames: int = 0
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
        self.existing_pairs = [overlap_to_start_end_pair(x) for x in overlaps_from_layer(layer)]
        self.current_pair_index = 0
        self.current_pair = None

    def has_room_for_note(self, analyzed_note: AnalyzedNote, same_frame_is_overlap: bool):
        if self.current_pair_index < len(self.existing_pairs):
            self.current_pair = self.existing_pairs[self.current_pair_index]

            start_frame = analyzed_note.action_start_frame

            while self.current_pair is not None and ((same_frame_is_overlap and self.current_pair[1] < start_frame) or (
                    not same_frame_is_overlap and self.current_pair[1] <= start_frame)):
                self.current_pair_index = self.current_pair_index + 1
                self.current_pair = self.existing_pairs[self.current_pair_index] if \
                    self.current_pair_index < len(self.existing_pairs) else None

        return not self.overlaps_last_pair(analyzed_note, same_frame_is_overlap)

    def overlaps_last_pair(self, analyzed_note: AnalyzedNote, same_frame_is_overlap: bool) -> bool:
        if self.current_pair is None:
            return False
        elif same_frame_is_overlap:
            return analyzed_note.action_start_frame <= self.current_pair[1] and \
                   analyzed_note.action_end_frame >= self.current_pair[0]
        else:
            return analyzed_note.action_start_frame < self.current_pair[1] and \
                   analyzed_note.action_end_frame > self.current_pair[0]


class ExistingNoteOverlaps:
    def __init__(self, existing_layers: List[Any], overlaps_from_layer: Callable[[Any], List[Any]],
                 overlap_to_start_end_pair: Callable[[Any], Tuple[int, int]]):
        """
        :param existing_layers: list of objects representing the existing layers
        :param overlaps_from_layer: function to get list of objects representing the existing overlaps on the layer
        :param overlap_to_start_end_pair: function to get the start and end frame of the overlap from the object
        """
        self.existing_layers = existing_layers
        self.overlaps_from_layer = overlaps_from_layer
        self.overlap_to_start_end_pair = overlap_to_start_end_pair
        self.layers = []
        self.existing_layers_iterator = iter(self.existing_layers)

    def get_layer(self, layer_index):
        while len(self.layers) <= layer_index:
            self.layers.append(self.calculate_next_layer())
        return self.layers[layer_index]

    def calculate_next_layer(self) -> Optional[ExistingNoteOverlapsLayer]:
        layer = next(self.existing_layers_iterator, None)
        if layer is not None:
            return ExistingNoteOverlapsLayer(layer, self.overlaps_from_layer, self.overlap_to_start_end_pair)
        else:
            return None


class NotesLayer:

    def __init__(self, existing_note_overlaps_layer: ExistingNoteOverlapsLayer, same_frame_is_overlap: bool):
        self.notes: List[AnalyzedNote] = []
        self.last_note_added: Optional[AnalyzedNote] = None
        self.existing_note_overlaps_layer = existing_note_overlaps_layer
        self.same_frame_is_overlap = same_frame_is_overlap

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
        elif self.same_frame_is_overlap:
            return analyzed_note.action_start_frame <= self.last_note_added.action_end_frame and \
                   analyzed_note.action_end_frame >= self.last_note_added.action_start_frame
        else:
            return analyzed_note.action_start_frame < self.last_note_added.action_end_frame and \
                   analyzed_note.action_end_frame > self.last_note_added.action_start_frame


class NoteCollectionMetaData:
    def __init__(self, loaded_midi_data: LoadedMidiData, frames_per_second: float,
                 frame_offset: int, start_at_note_end: bool, scale_factor: Optional[float],
                 non_scaled_action_length: Optional[int]):
        self.frame_offset = frame_offset
        self.scale_factor = scale_factor  # if None then no scaling, use action length instead
        self.start_at_note_end = start_at_note_end
        self.frames_per_second = frames_per_second
        self.loaded_midi_data = loaded_midi_data
        self.non_scaled_action_length = non_scaled_action_length

    @staticmethod
    def from_note_action_property(loaded_midi_data: LoadedMidiData, context, note_action_property,
                                  non_scaled_action_length, additional_frame_offset=0, override_action_length=None):
        midi_data_property = loaded_midi_data.get_midi_data_property(context)
        if override_action_length is not None:
            non_scaled_action_length = override_action_length if non_scaled_action_length is None else \
                max(non_scaled_action_length, override_action_length)
        scale_factor = note_action_property.scale_factor if note_action_property.sync_length_with_notes else None
        return NoteCollectionMetaData(loaded_midi_data, context.scene.render.fps,
                                      midi_data_property.midi_frame_start + note_action_property.midi_frame_offset +
                                      additional_frame_offset, note_action_property.copy_to_note_end,
                                      scale_factor, non_scaled_action_length)


class NoteCollectionOverlapStrategy:
    def __init__(self, top_down: bool, skip_existing: bool, same_frame_is_overlap: bool):
        """
        :param top_down: overlap check starting at top layer working down if true, bottom layer working up if False
        :param skip_existing: if true, skip notes that overlap existing actions on the first layer
          (instead of creating new layers for those notes)
        :param same_frame_is_overlap: if true, an action that ends on the same frame that the next action starts will be
         considered overlapping
        """
        self.top_down = top_down
        self.skip_existing = skip_existing
        self.same_frame_is_overlap = same_frame_is_overlap


class NoteCollectionFilter:
    def __init__(self, filter_groups_list, default_pitch: int, default_pitch_filter: bool, include_custom_filters: bool,
                 context):
        """
        :param filter_groups_list: list of filter group properties
        :param default_pitch: default pitch to use if no pitch filters
        :param default_pitch_filter: if true, filters by default pitch of no pitch filters
        :param include_custom_filters: if false, does not filter by filter groups
        :param context: blender Context
        """
        self.filter_groups_list = filter_groups_list
        self.default_pitch = default_pitch
        self.default_pitch_filter = default_pitch_filter
        self.include_custom_filters = include_custom_filters
        self.context = context

    def filter_notes(self, analyzed_notes: List[AnalyzedNote]):
        return NoteFilterImplementations.filter_notes(analyzed_notes, self.filter_groups_list, self.default_pitch,
                                                      include_custom_filters=self.include_custom_filters,
                                                      default_pitch_filter=self.default_pitch_filter,
                                                      context=self.context)


class NoteCollection:

    def __init__(self, notes: List[Note], note_collection_meta_data: NoteCollectionMetaData,
                 overlap_strategy: NoteCollectionOverlapStrategy,
                 note_collection_filter: Optional[NoteCollectionFilter],
                 existing_note_overlaps: Optional[ExistingNoteOverlaps] = None):
        self.notes_layers: List[NotesLayer] = []
        self.all_notes: List[AnalyzedNote] = []  # all notes before applying filters
        self.filtered_notes: List[AnalyzedNote] = []  # all notes after applying filters
        self.frames_per_second = note_collection_meta_data.frames_per_second
        self.frame_offset = note_collection_meta_data.frame_offset
        self.scale_factor = note_collection_meta_data.scale_factor
        self.start_at_note_end = note_collection_meta_data.start_at_note_end
        self.raw_notes = notes
        self.loaded_midi_data = note_collection_meta_data.loaded_midi_data
        self.non_scaled_action_length = note_collection_meta_data.non_scaled_action_length
        self.existing_note_overlaps = existing_note_overlaps
        self.overlap_strategy = overlap_strategy
        self.note_collection_filter = note_collection_filter

        self.__calculate_notes()

    def __calculate_notes(self):
        # pre-populate all layers with existing overlaps
        if self.existing_note_overlaps is not None:
            for i in range(len(self.existing_note_overlaps.existing_layers)):
                self.create_new_layer(self.notes_layers)
        for note in self.raw_notes:
            analyzed_note = self.create_analyzed_note(note=note, use_file_tempo=self.loaded_midi_data.use_file_tempo,
                                                      ms_per_tick=self.loaded_midi_data.ms_per_tick,
                                                      frames_per_second=self.frames_per_second,
                                                      frame_offset=self.frame_offset,
                                                      scale_factor=self.scale_factor,
                                                      start_at_note_end=self.start_at_note_end,
                                                      non_scaled_action_length=self.non_scaled_action_length)
            self.all_notes.append(analyzed_note)
        self.filtered_notes = self.all_notes if self.note_collection_filter is None else \
            self.note_collection_filter.filter_notes(self.all_notes)
        for analyzed_note in self.filtered_notes:
            self.add_note_to_layer(analyzed_note, self.notes_layers, self.overlap_strategy.top_down,
                                   self.overlap_strategy.skip_existing)

    def add_note_to_layer(self, analyzed_note: AnalyzedNote, layers: List[NotesLayer], top_down_overlap: bool,
                          skip_existing_overlaps: bool):
        iterator = reversed(layers) if top_down_overlap else layers
        first_layer: Optional[NotesLayer] = layers[0] if len(layers) > 0 else None
        if skip_existing_overlaps and first_layer is not None and first_layer.overlaps_existing(analyzed_note):
            return

        # check for existing layer with room
        if top_down_overlap:
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

        # no existing layer with room, add a new layer
        note_added = False
        while not note_added:
            new_layer = self.create_new_layer(layers)
            if first_layer is None:
                first_layer = new_layer
                if skip_existing_overlaps and first_layer.overlaps_existing(analyzed_note):
                    return
            if new_layer.has_room_for_note(analyzed_note):
                new_layer.add_note(analyzed_note)
                note_added = True

    def create_new_layer(self, layers):
        new_layer = NotesLayer(self.existing_note_overlaps.get_layer(len(self.notes_layers))
                               if self.existing_note_overlaps is not None else None,
                               self.overlap_strategy.same_frame_is_overlap)
        layers.append(new_layer)
        return new_layer

    def notes_on_first_layer(self) -> List[AnalyzedNote]:
        return self.notes_layers[0].notes if len(self.notes_layers) > 0 else []

    def create_analyzed_note(self, note: Note, use_file_tempo: bool, ms_per_tick: float, frames_per_second: float,
                             frame_offset: int, scale_factor: float, start_at_note_end: bool,
                             non_scaled_action_length: Optional[int]) -> AnalyzedNote:
        return AnalyzedNote(note=note, use_file_tempo=use_file_tempo,
                            ms_per_tick=ms_per_tick,
                            frames_per_second=frames_per_second,
                            frame_offset=frame_offset,
                            scale_factor=scale_factor,
                            start_at_note_end=start_at_note_end,
                            non_scaled_action_length=non_scaled_action_length)
