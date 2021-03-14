if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PropertyUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PitchUtils)
else:
    from . import PropertyUtils
    from . import PitchUtils

from abc import abstractmethod, ABC
from typing import List, Tuple, Callable

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
    def filtered_notes(self, notes: List[Tuple[int, Note]], context) -> List[Tuple[int, Note]]:
        """
        :return: filtered list of notes paired to original indices
        """
        pass

    @staticmethod
    @abstractmethod
    def draw_ui(parent_layout, note_filter_property):
        pass

    def compare_values(self, value1, value2):
        return PropertyUtils.compare(self.note_filter.comparison_operator, value1, value2)

    def filter_by_callable(self, notes: List[Tuple[int, Note]], filter_callable: Callable[[Note], bool]) -> List[
        Tuple[int, Note]]:
        return [note_pair for note_pair in notes if filter_callable(note_pair[1])]
        pass

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
    def draw_time_comparision(parent_layout, note_filter_property, int_value_property, float_value_property,
                              time_unit_property):
        row1, row2 = NoteFilterBase.split_into_rows(parent_layout, 0.35)
        row1.prop(note_filter_property, "comparison_operator", text='')
        value_property = NoteFilterBase.time_value_property(getattr(note_filter_property, time_unit_property),
                                                            int_value_property, float_value_property)
        row2.prop(note_filter_property, value_property, text='')
        row2.prop(note_filter_property, time_unit_property, text='')


class PitchFilter(NoteFilterBase):
    ID = "note_pitch_filter"
    NAME = "Pitch"
    DESCRIPTION = "Filter by the note's pitch. (This overrides the selected note.)"
    NUMBER = 2

    def __init__(self, note_filter_property):
        super().__init__(note_filter_property)
        self.pitch = None

    def filtered_notes(self, notes: List[Tuple[int, Note]], context) -> List[Tuple[int, Note]]:
        if self.pitch is None:
            self.pitch = PitchUtils.note_pitch_from_id(self.note_filter.note_pitch)
        return self.filter_by_callable(notes, lambda note: self.compare_values(note.pitch, self.pitch))

    @staticmethod
    def draw_ui(parent_layout, note_filter_property):
        NoteFilterBase.draw_comparison_and_value(parent_layout, note_filter_property, "note_pitch",
                                                 "note_pitch_search_string")


class StartTime(NoteFilterBase):
    ID = "note_start_time_relative_frames"
    NAME = "Relative Start Time"
    DESCRIPTION = "Filter notes by start time (relative to the start of the midi file)"
    NUMBER = 3

    def filtered_notes(self, notes: List[Tuple[int, Note]], context) -> List[Tuple[int, Note]]:
        start_time_frames = \
            PropertyUtils.time_in_frames(
                getattr(self.note_filter, NoteFilterBase.time_value_property(
                    self.note_filter.time_unit, "non_negative_int", "non_negative_number")),
                self.note_filter.time_unit,
                context)
        return self.filter_by_callable(notes,
                                       lambda note: self.compare_values(
                                           PropertyUtils.ms_to_frames(note.startTime, context), start_time_frames))

    @staticmethod
    def draw_ui(parent_layout, note_filter_property):
        NoteFilterBase.draw_time_comparision(parent_layout, note_filter_property, "non_negative_int",
                                             "non_negative_number", "time_unit")


class NoteLength(NoteFilterBase):
    ID = "note_length_filter"
    NAME = "Note Length"
    DESCRIPTION = "Filter notes by length"
    NUMBER = 1

    def filtered_notes(self, notes: List[Tuple[int, Note]], context):
        note_length_frames = PropertyUtils.time_in_frames(
            getattr(self.note_filter, NoteFilterBase.time_value_property(
                self.note_filter.time_unit, "non_negative_int", "non_negative_number")),
            self.note_filter.time_unit, context)
        return self.filter_by_callable(notes, lambda note: self.compare_values(
            PropertyUtils.ms_to_frames(note.length(), context), note_length_frames))

    @staticmethod
    def draw_ui(parent_layout, note_filter_property):
        NoteFilterBase.draw_time_comparision(parent_layout, note_filter_property, "non_negative_int",
                                             "non_negative_number", "time_unit")


class NoteVelocity(NoteFilterBase):
    ID = "note_velocity_filter"
    NAME = "Velocity"
    DESCRIPTION = "Filter notes by velocity"
    NUMBER = 4

    def filtered_notes(self, notes: List[Tuple[int, Note]], context):
        return self.filter_by_callable(notes,
                                       lambda note: self.compare_values(note.velocity, self.note_filter.int_0_to_127))

    @staticmethod
    def draw_ui(parent_layout, note_filter_property):
        NoteFilterBase.draw_comparison_and_value(parent_layout, note_filter_property, "int_0_to_127")


class AlternationFilter(NoteFilterBase):
    ID = "note_alternation_filter"
    NAME = "Every"
    DESCRIPTION = "Filter notes by an alternation pattern. " \
                  "(For example only every fourth note, starting with the third note.)"
    NAME_DISPLAY_WEIGHT = 0.2
    NUMBER = 0

    def filtered_notes(self, notes: List[Tuple[int, Note]], context) -> List[Tuple[int, Note]]:
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


FILTER_REGISTRY = [AlternationFilter, NoteLength, PitchFilter, StartTime, NoteVelocity]
# map id to filter class
ID_TO_FILTER = {note_filter.ID: note_filter for note_filter in FILTER_REGISTRY}
# notes filters for enum property
FILTER_ENUM_PROPERTY_ITEMS = [(note_filter.ID, note_filter.NAME, note_filter.DESCRIPTION, note_filter.NUMBER) for
                              note_filter in FILTER_REGISTRY]


def __notes_passing_filter(notes: List[Note], filter_group_property, default_pitch: int, context) -> \
        List[Tuple[int, Note]]:
    """
    :param notes: list of notes
    :param filter_group_property: filter group property
    :return: list of notes passing the filter paired with their indices before filtering
    """
    notes_paired_to_index = [(i, notes[i]) for i in range(len(notes))]
    note_filters = [ID_TO_FILTER[note_filter_property.filter_type](note_filter_property) for
                    note_filter_property in filter_group_property.note_filters]
    # apply default pitch as pitch filter if no pitch filters are part of the filter groups
    if not any(isinstance(note_filter, PitchFilter) for note_filter in note_filters):
        notes_paired_to_index = [note_index_pair for note_index_pair in notes_paired_to_index if
                                 note_index_pair[1].pitch == default_pitch]
    for note_filter in note_filters:
        if isinstance(note_filter, PitchFilter) and PitchUtils.note_id_is_selected_note(
                note_filter.note_filter.note_pitch):
            note_filter.pitch = default_pitch
        notes_paired_to_index = note_filter.filtered_notes(notes_paired_to_index, context)
    return notes_paired_to_index


def filter_notes(notes: List[Note], filter_groups_list, default_pitch: int, include_custom_filters, context) -> List[
    Note]:
    """
    :param notes: list of notes
    :param filter_groups_list: list of filter groups
    :param default_pitch: pitch to filter by if no other filters are defined
    :param include_custom_filters: if false will only filter by pitch
    :param context: the context
    :return: filtered list of notes
    """
    if include_custom_filters and len(filter_groups_list) > 0:
        grouped_filtered_note_pairs = [__notes_passing_filter(notes, filter_group, default_pitch, context) for
                                       filter_group in filter_groups_list]
        all_passing_note_pairs = [note_pair for filtered_note_pairs in grouped_filtered_note_pairs for note_pair in
                                  filtered_note_pairs]
        all_passing_note_pairs.sort(key=lambda note_index_pair: note_index_pair[0])
        return list(OrderedDict(all_passing_note_pairs).values())
    else:
        # no filters, filter by pitch
        return [note for note in notes if note.pitch == default_pitch]
    pass
