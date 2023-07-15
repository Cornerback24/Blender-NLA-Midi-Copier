if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PropertyUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PitchUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteCollectionUtils)
else:
    from . import PropertyUtils
    from . import PitchUtils
    from . import NoteCollectionUtils
    from .i18n import i18n

import bpy
from abc import abstractmethod, ABC
from typing import List, Tuple, Callable

from .NoteCollectionUtils import NotesLayer, OverlapChecker, AnalyzedNote
from .midi_analysis.Note import Note
from collections import OrderedDict


class NoteFilterBase(ABC):
    ID = None  # id of the filter
    NAME = None  # name of the filter
    DESCRIPTION = None  # Description of the filter
    NAME_DISPLAY_WEIGHT = 0.37  # percentage of the row on the ui that will be allocated to the filter type property
    NUMBER = 0  # Number for storing in enum property. Must be unique for each enum class.

    def __init__(self, note_filter_property):
        self.note_filter = note_filter_property

    @abstractmethod
    def filtered_notes(self, notes: List[Tuple[int, 'AnalyzedNote']], context) -> List[Tuple[int, 'AnalyzedNote']]:
        """
        :return: filtered list of notes paired to original indices
        """
        pass

    @staticmethod
    @abstractmethod
    def draw_ui(parent_layout, note_filter_property):
        pass

    def compare_values(self, value1, value2, comparison_operator=None):
        return PropertyUtils.compare(
            comparison_operator if comparison_operator is not None else self.note_filter.comparison_operator,
            value1, value2)

    def filter_by_callable(self, notes: List[Tuple[int, 'AnalyzedNote']],
                           filter_callable: Callable[['AnalyzedNote'], bool]) -> List[Tuple[int, 'AnalyzedNote']]:
        return [note_pair for note_pair in notes if filter_callable(note_pair[1])]

    def filter_by_note_callable(self, notes: List[Tuple[int, 'AnalyzedNote']],
                                filter_callable: Callable[[Note], bool]) -> List[Tuple[int, 'AnalyzedNote']]:
        return [note_pair for note_pair in notes if filter_callable(note_pair[1].note)]

    @staticmethod
    def split_into_rows(parent_layout, factor: float):
        split = parent_layout.row().split(factor=factor)
        return split.row(), split.row()

    @staticmethod
    def draw_comparison_and_value(parent_layout, note_filter_property, value_property, unit_property=None):
        row1, row2 = NoteFilterBase.split_into_rows(parent_layout, 0.35)
        row1.prop(note_filter_property, "comparison_operator", text='')
        row2.prop(note_filter_property, value_property, text='')
        if unit_property is not None:
            row2.prop(note_filter_property, unit_property, text='')

    @staticmethod
    def time_value_property(time_unit, int_value_property, float_value_property):
        """
        :param time_unit: unit of time
        :param int_value_property: property if the unit corresponds to integer times (such as frames)
        :param float_value_property: property if the unit corresponds to float times (such as seconds)
        :return: the property for the time value
        """
        return int_value_property if time_unit == "frames" else float_value_property

    @staticmethod
    def draw_time_comparison(parent_layout, note_filter_property, int_value_property, float_value_property,
                             time_unit_property):
        row1, row2 = NoteFilterBase.split_into_rows(parent_layout, 0.35)
        row1.prop(note_filter_property, "comparison_operator", text='')
        value_property = NoteFilterBase.time_value_property(getattr(note_filter_property, time_unit_property),
                                                            int_value_property, float_value_property)
        row2.prop(note_filter_property, value_property, text='')
        row2.prop(note_filter_property, time_unit_property, text='')


class PitchFilter(NoteFilterBase):
    ID = "note_pitch_filter"
    NAME = i18n.get_key(i18n.PITCH)
    DESCRIPTION = i18n.get_key(i18n.PITCH_FILTER_DESCRIPTION)
    NUMBER = 2

    def __init__(self, note_filter_property):
        super().__init__(note_filter_property)
        self.pitch = None

    def filtered_notes(self, notes: List[Tuple[int, 'AnalyzedNote']], context) -> List[Tuple[int, 'AnalyzedNote']]:
        if self.pitch is None:
            self.pitch = PitchUtils.note_pitch_from_id(self.note_filter.note_pitch)
        return self.filter_by_note_callable(notes, lambda note: self.compare_values(note.pitch, self.pitch))

    @staticmethod
    def draw_ui(parent_layout, note_filter_property):
        NoteFilterBase.draw_comparison_and_value(parent_layout, note_filter_property, "note_pitch",
                                                 "note_pitch_search_string")


class RelativeStartTime(NoteFilterBase):
    ID = "note_start_time_relative_frames"
    NAME = i18n.get_key(i18n.RELATIVE_START_TIME)
    DESCRIPTION = i18n.get_key(i18n.RELATIVE_START_TIME_FILTER_DESCRIPTION)
    NUMBER = 3

    def filtered_notes(self, notes: List[Tuple[int, 'AnalyzedNote']], context) -> List[Tuple[int, 'AnalyzedNote']]:
        start_time_frames = \
            PropertyUtils.time_in_frames(
                getattr(self.note_filter, NoteFilterBase.time_value_property(
                    self.note_filter.time_unit, "non_negative_int", "non_negative_number")),
                self.note_filter.time_unit,
                context)
        return self.filter_by_note_callable(notes,
                                            lambda note: self.compare_values(
                                                PropertyUtils.ms_to_frames(note.startTime, context), start_time_frames))

    @staticmethod
    def draw_ui(parent_layout, note_filter_property):
        NoteFilterBase.draw_time_comparison(parent_layout, note_filter_property, "non_negative_int",
                                            "non_negative_number", "time_unit")


class StartTime(NoteFilterBase):
    ID = "note_start_time_frames"
    NAME = i18n.get_key(i18n.START_TIME)
    DESCRIPTION = i18n.get_key(i18n.START_TIME_FILTER_DESCRIPTION)
    NUMBER = 5

    def filtered_notes(self, notes: List[Tuple[int, 'AnalyzedNote']], context) -> List[Tuple[int, 'AnalyzedNote']]:
        start_time_frames = \
            PropertyUtils.time_in_frames(
                getattr(self.note_filter, NoteFilterBase.time_value_property(
                    self.note_filter.time_unit, "non_negative_int", "non_negative_number")),
                self.note_filter.time_unit,
                context)
        return self.filter_by_callable(notes, lambda note: self.compare_values(
            note.note_start_frame, start_time_frames))

    @staticmethod
    def draw_ui(parent_layout, note_filter_property):
        NoteFilterBase.draw_time_comparison(parent_layout, note_filter_property, "non_negative_int",
                                            "non_negative_number", "time_unit")


class NoteLength(NoteFilterBase):
    ID = "note_length_filter"
    NAME = i18n.get_key(i18n.NOTE_LENGTH)
    DESCRIPTION = i18n.get_key(i18n.NOTE_LENGTH_FILTER_DESCRIPTION)
    NUMBER = 1

    def filtered_notes(self, notes: List[Tuple[int, 'AnalyzedNote']], context):
        note_length_frames = PropertyUtils.time_in_frames(
            getattr(self.note_filter, NoteFilterBase.time_value_property(
                self.note_filter.time_unit, "non_negative_int", "non_negative_number")),
            self.note_filter.time_unit, context)
        return self.filter_by_callable(notes, lambda note: self.compare_values(
            note.note_length_frames, note_length_frames))

    @staticmethod
    def draw_ui(parent_layout, note_filter_property):
        NoteFilterBase.draw_time_comparison(parent_layout, note_filter_property, "non_negative_int",
                                            "non_negative_number", "time_unit")


class NoteVelocity(NoteFilterBase):
    ID = "note_velocity_filter"
    NAME = i18n.get_key(i18n.VELOCITY)
    DESCRIPTION = i18n.get_key(i18n.VELOCITY_FILTER_DESCRIPTION)
    NUMBER = 4

    def filtered_notes(self, notes: List[Tuple[int, 'AnalyzedNote']], context):
        return self.filter_by_note_callable(notes,
                                            lambda note: self.compare_values(note.velocity,
                                                                             self.note_filter.int_0_to_127))

    @staticmethod
    def draw_ui(parent_layout, note_filter_property):
        NoteFilterBase.draw_comparison_and_value(parent_layout, note_filter_property, "int_0_to_127")


class AlternationFilter(NoteFilterBase):
    ID = "note_alternation_filter"
    NAME = i18n.get_key(i18n.EVERY)
    DESCRIPTION = i18n.get_key(i18n.ALTERNATION_FILTER_DESCRIPTION)
    NAME_DISPLAY_WEIGHT = 0.2
    NUMBER = 0

    def filtered_notes(self, notes: List[Tuple[int, 'AnalyzedNote']], context) -> List[Tuple[int, 'AnalyzedNote']]:
        alternation_factor = self.note_filter.positive_int
        first_note_index = self.note_filter.positive_int_2 - 1
        filtered_note_pairs = []
        for i in range(len(notes)):
            if i >= first_note_index and (i - first_note_index) % alternation_factor == 0:
                filtered_note_pairs.append(notes[i])
        return filtered_note_pairs

    @staticmethod
    def draw_ui(parent_layout, note_filter_property):
        row1, row2 = NoteFilterBase.split_into_rows(parent_layout, .3)
        row1.prop(note_filter_property, "positive_int", text='')
        row2_1, row2_2 = NoteFilterBase.split_into_rows(row2, .6)
        row2_1.label(text='notes, starting with note')
        row2_2.prop(note_filter_property, "positive_int_2", text='')


class OverlapFilter(NoteFilterBase):
    ID = "note_overlap_filter"
    NAME = i18n.get_key(i18n.OVERLAP)
    DESCRIPTION = i18n.get_key(i18n.OVERLAP_FILTER_DESCRIPTION)
    NUMBER = 6

    def filtered_notes(self, notes: List[Tuple[int, 'AnalyzedNote']], context) -> List[Tuple[int, 'AnalyzedNote']]:
        notes_layers: List[NotesLayer] = []
        # second int is overlap count, third list acts as mutable pair
        calculated_layers: List[List[List[Tuple[int, AnalyzedNote], int]]] = []
        # create note layers to determine overlaps
        for note_index_pair in notes:
            note_added = False
            analyzed_note = note_index_pair[1]
            for i in range(len(notes_layers)):
                if not note_added:
                    notes_layer = notes_layers[i]
                    if notes_layer.has_room_for_note(analyzed_note):
                        notes_layer.add_note(analyzed_note)
                        calculated_layers[i].append([note_index_pair, i + 1])
                        note_added = True
            if not note_added:
                notes_layer = NotesLayer(None, False,
                                         frame_length_for_overlap=self.note_filter.positive_int_3 if
                                         self.note_filter.calculate_overlap_by_frames else None)
                notes_layer.add_note(analyzed_note)
                notes_layers.append(notes_layer)
                calculated_layers.append([[note_index_pair, len(calculated_layers) + 1]])

        # count overlaps
        overlap_checkers: List[OverlapChecker] = \
            [OverlapChecker([(note.action_start_frame, note.action_end_frame) for note in notes_layer.notes]) for
             notes_layer in notes_layers]
        for i in range(len(calculated_layers)):
            for overlap_checker in overlap_checkers:
                overlap_checker.reset_index()
            calculated_layer = calculated_layers[i]
            for j in range(i + 1, len(calculated_layers)):
                overlap_checker = overlap_checkers[j]
                for calculated_overlap_count_pair in calculated_layer:
                    analyzed_note = calculated_overlap_count_pair[0][1]
                    if not overlap_checker.has_room_for_pair(
                            (analyzed_note.action_start_frame, analyzed_note.action_end_frame), False):
                        calculated_overlap_count_pair[1] += 1

        note_index_pairs = []
        # return result based on overlap layer
        for i in range(len(calculated_layers)):
            calculated_layer = calculated_layers[i]
            for calculated_overlap_count_pair in calculated_layer:
                # First layer is layer 1. Note with no overlaps has count 1.
                if self.compare_values(i + 1, self.note_filter.positive_int) and \
                        self.compare_values(calculated_overlap_count_pair[1], self.note_filter.positive_int_2,
                                            self.note_filter.comparison_operator2):
                    note_index_pairs.append(calculated_overlap_count_pair[0])

        return note_index_pairs

    @staticmethod
    def draw_ui(parent_layout, note_filter_property):
        col = parent_layout.column(align=True)
        row1, row2 = NoteFilterBase.split_into_rows(col, .4)
        row1.label(text=i18n.get_key(i18n.LAYER))
        row2_1, row2_2 = NoteFilterBase.split_into_rows(row2, .6)
        row2_1.prop(note_filter_property, "comparison_operator", text='')
        row2_2.prop(note_filter_property, "positive_int", text='')
        row1, row2 = NoteFilterBase.split_into_rows(col, .4)
        row1.label(text=i18n.get_key(i18n.COUNT))
        row2_1, row2_2 = NoteFilterBase.split_into_rows(row2, .6)
        row2_1.prop(note_filter_property, "comparison_operator2", text='')
        row2_2.prop(note_filter_property, "positive_int_2", text='')
        row1, row2 = NoteFilterBase.split_into_rows(col, .6)
        row2_1, row2_2 = NoteFilterBase.split_into_rows(row2, .4)
        row1.prop(note_filter_property, "calculate_overlap_by_frames")
        row2_2.enabled = note_filter_property.calculate_overlap_by_frames
        row2_2.prop(note_filter_property, "positive_int_3", text='')


FILTER_REGISTRY = [AlternationFilter, NoteLength, OverlapFilter, PitchFilter, RelativeStartTime, StartTime,
                   NoteVelocity]
# map id to filter class
ID_TO_FILTER = {note_filter.ID: note_filter for note_filter in FILTER_REGISTRY}
# notes filters for enum property
FILTER_ENUM_PROPERTY_ITEMS = [(note_filter.ID, note_filter.NAME, note_filter.DESCRIPTION, note_filter.NUMBER) for
                              note_filter in FILTER_REGISTRY]


def __notes_passing_filter(notes: List['AnalyzedNote'], filter_group_property, default_pitch: int,
                           default_pitch_filter: bool, context) -> \
        List[Tuple[int, 'AnalyzedNote']]:
    """
    :param notes: list of notes
    :param filter_group_property: filter group property
    :return: list of notes passing the filter paired with their indices before filtering
    """
    notes_paired_to_index = [(i, notes[i]) for i in range(len(notes))]
    note_filters = [ID_TO_FILTER[note_filter_property.filter_type](note_filter_property) for
                    note_filter_property in filter_group_property.note_filters]
    # apply default pitch as pitch filter if no pitch filters are part of the filter groups
    if default_pitch_filter and not any(isinstance(note_filter, PitchFilter) for note_filter in note_filters):
        notes_paired_to_index = [note_index_pair for note_index_pair in notes_paired_to_index if
                                 note_index_pair[1].note.pitch == default_pitch]
    for note_filter in note_filters:
        if isinstance(note_filter, PitchFilter) and PitchUtils.note_id_is_selected_note(
                note_filter.note_filter.note_pitch):
            note_filter.pitch = default_pitch
        notes_paired_to_index = note_filter.filtered_notes(notes_paired_to_index, context)
    notes_paired_to_index.sort(key=lambda note_index_pair: note_index_pair[0])
    return notes_paired_to_index


def filter_notes(notes: List['AnalyzedNote'], filter_groups_list, default_pitch: int, include_custom_filters: bool,
                 default_pitch_filter: bool, context) -> List['AnalyzedNote']:
    """
    :param notes: list of notes
    :param filter_groups_list: list of filter groups
    :param default_pitch: pitch to filter by if no other filters are defined
    :param include_custom_filters: if false will only filter by pitch
    :param context: the context
    :param default_pitch_filter: filter by default pitch if no pitch filters
    :return: filtered list of notes
    """
    if include_custom_filters and len(filter_groups_list) > 0:
        grouped_filtered_note_pairs = [
            __notes_passing_filter(notes, filter_group, default_pitch, default_pitch_filter, context) for
            filter_group in filter_groups_list]
        all_passing_note_pairs = [note_pair for filtered_note_pairs in grouped_filtered_note_pairs for note_pair in
                                  filtered_note_pairs]
        all_passing_note_pairs.sort(key=lambda note_index_pair: note_index_pair[0])
        return list(OrderedDict(all_passing_note_pairs).values())
    else:
        return [analyzed_note for analyzed_note in notes if
                (analyzed_note.note.pitch == default_pitch or not default_pitch_filter)]
