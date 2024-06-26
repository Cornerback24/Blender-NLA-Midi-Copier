if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from .i18n import i18n

import bpy
from bpy.props import StringProperty, EnumProperty
from bpy.app import version as blender_version
from typing import Any
import math


def instrument_selected_note_property(instrument):
    """
    :param instrument: instrument
    :return: the instrument's selected note property
    """
    note_id = int(instrument.selected_note_id)
    instrument_note_property = next((x for x in instrument.notes if x.note_id == note_id), None)
    return instrument_note_property


def selected_note_property(loaded_midi_data, is_part_of_instrument, action_index, context):
    """
    :param loaded_midi_data: LoadedMidiData
    :param is_part_of_instrument: true if the note is part of an instrument, false if it is the note from the Midi panel
    :param context: the context
    :param action_index: the index of the NoteActionProperty in the instrument
    :return: the selected NoteActionProperty  (None if no note selected)
    """
    if is_part_of_instrument:
        selected_instrument = loaded_midi_data.selected_instrument(context)
        selected_note = instrument_selected_note_property(selected_instrument).actions[action_index]
    else:
        selected_note = loaded_midi_data.selected_note_action_property(context)
    return selected_note


def get_note_action_property(instrument, note_id: int):
    instrument_note_property = next((x for x in instrument.notes if x.note_id == note_id), None)
    if instrument_note_property is None:
        instrument_note_property = instrument.notes.add()
        instrument_note_property.note_id = note_id

    note_action_property = instrument_note_property.actions.add()
    note_action_property.name = i18n.concat(i18n.get_text(i18n.ACTION), str(len(instrument_note_property.actions)))
    return note_action_property


def copy_note_action_property(copy_from, copy_to, id_properties_dictionary):
    """
    :param copy_from: Note action property to copy from
    :param copy_to: Note action property to copy to
    :param id_properties_dictionary: key is NoteActionProperty.id_type,
     value is (NoteActionProperty field name, Action id_root, enum number)
    """
    copy_to.id_type = copy_from.id_type
    copy_to.action = copy_from.action
    copy_to.midi_frame_offset = copy_from.midi_frame_offset
    copy_to.nla_track_name = copy_from.nla_track_name
    copy_to.duplicate_object_on_overlap = copy_from.duplicate_object_on_overlap
    copy_to.on_overlap = copy_from.on_overlap
    copy_to.blend_mode = copy_from.blend_mode
    copy_to.sync_length_with_notes = copy_from.sync_length_with_notes
    copy_to.copy_to_note_end = copy_from.copy_to_note_end
    copy_to.add_filters = copy_from.add_filters
    copy_to.filters_expanded = copy_from.filters_expanded
    copy_to.action_length = copy_from.action_length
    copy_to.scale_factor = copy_from.scale_factor
    copy_to.sync_length_action_timing_mode = copy_from.sync_length_action_timing_mode
    copy_from_note_filter_groups = copy_from.note_filter_groups
    copy_to_note_filter_groups = copy_to.note_filter_groups
    copy_filters(copy_from_note_filter_groups, copy_to_note_filter_groups)
    animated_object_property = id_properties_dictionary[copy_from.id_type][0]
    setattr(copy_to, animated_object_property, getattr(copy_from, animated_object_property))


def copy_filters(copy_from_note_filter_groups, copy_to_note_filter_groups):
    copy_to_note_filter_groups.clear()
    for copy_from_filter_group in copy_from_note_filter_groups:
        copy_to_filter_group = copy_to_note_filter_groups.add()
        copy_to_filter_group.all_pitches = copy_from_filter_group.all_pitches
        for copy_from_filter in copy_from_filter_group.note_filters:
            copy_to_filter = copy_to_filter_group.note_filters.add()
            copy_to_filter.filter_type = copy_from_filter.filter_type
            copy_to_filter.comparison_operator = copy_from_filter.comparison_operator
            copy_to_filter.comparison_operator2 = copy_from_filter.comparison_operator2
            copy_to_filter.note_pitch = copy_from_filter.note_pitch
            copy_to_filter.non_negative_int = copy_from_filter.non_negative_int
            copy_to_filter.positive_int = copy_from_filter.positive_int
            copy_to_filter.positive_int_2 = copy_from_filter.positive_int_2
            copy_to_filter.positive_int_3 = copy_from_filter.positive_int_3
            copy_to_filter.int_0_to_127 = copy_from_filter.int_0_to_127
            copy_to_filter.non_negative_number = copy_from_filter.non_negative_number
            copy_to_filter.time_unit = copy_from_filter.time_unit
            copy_to_filter.calculate_overlap_by_frames = copy_from_filter.calculate_overlap_by_frames


def compare_filters(filter_groups_1, filter_groups_2):
    if len(filter_groups_1) != len(filter_groups_2):
        return False
    for (filter_group_1, filter_group_2) in zip(filter_groups_1, filter_groups_2):
        if len(filter_group_1.note_filters) != len(filter_group_2.note_filters) or \
                filter_group_1.all_pitches != filter_group_2.all_pitches:
            return False
        for (note_filter_1, note_filter_2) in zip(filter_group_1.note_filters, filter_group_2.note_filters):
            filters_equal = \
                note_filter_1.filter_type == note_filter_2.filter_type and \
                note_filter_1.comparison_operator == note_filter_2.comparison_operator and \
                note_filter_1.comparison_operator2 == note_filter_2.comparison_operator2 and \
                note_filter_1.note_pitch == note_filter_2.note_pitch and \
                note_filter_1.non_negative_int == note_filter_2.non_negative_int and \
                note_filter_1.positive_int == note_filter_2.positive_int and \
                note_filter_1.positive_int_2 == note_filter_2.positive_int_2 and \
                note_filter_1.positive_int_3 == note_filter_2.positive_int_3 and \
                note_filter_1.int_0_to_127 == note_filter_2.int_0_to_127 and \
                note_filter_1.non_negative_number == note_filter_2.non_negative_number and \
                note_filter_1.time_unit == note_filter_2.time_unit and \
                note_filter_1.calculate_overlap_by_frames == note_filter_2.calculate_overlap_by_frames
            if not filters_equal:
                return False
    return True


def compare(comparison_operator: str, a: Any, b: Any) -> bool:
    if comparison_operator == "less_than":
        return a < b
    elif comparison_operator == "less_than_or_equal_to":
        return a <= b
    elif comparison_operator == "equal_to":
        return a == b
    elif comparison_operator == "greater_than_or_equal_to":
        return a >= b
    elif comparison_operator == "greater_than":
        return a > b
    else:
        raise ValueError(f"{comparison_operator} comparison operator not supported")


def time_in_frames(time, time_unit: str, context) -> int:
    if time_unit == "frames":
        return time
    elif time_unit == "seconds":
        frames_per_second = context.scene.render.fps
        return math.floor(time * frames_per_second)
    else:
        raise ValueError(f"{time_unit} time unit not supported")


def ms_to_frames(ms: float, context) -> int:
    frames_per_second = context.scene.render.fps
    return math.floor(ms / 1000 * frames_per_second)


def note_updated_function(note_attribute, note_filter_attribute, get_notes_list):
    def note_updated(data, context):
        note: str = getattr(data, note_attribute)
        current_note_filter = getattr(data, note_filter_attribute)
        if note is not None:
            # Set to midi note number if current filter is blank or number. If current filter is non-numeric (note name)
            # then set to note name
            if current_note_filter.isdigit() or not current_note_filter:
                setattr(data, note_filter_attribute, note)
            else:
                notes_list = get_notes_list(data, context)
                for note_enum in notes_list:
                    if note == note_enum[0]:
                        # remove extra information, such as instrument action count
                        setattr(data, note_filter_attribute, note_enum[1].split()[0])
                        return
                setattr(data, note_filter_attribute, note)

    return lambda data, context: note_updated(data, context)


def find_matching_note(notes_list_enums, note_string):
    filter_string_is_digit = note_string.isdigit()
    # if digit, then check string equals note pitch, else check note display contains string
    if filter_string_is_digit:
        for note in notes_list_enums:
            if note_string == note[0]:
                return note
    else:
        matches = [note for note in notes_list_enums if note_string.lower() in note[1].lower()]
        if len(matches) == 1:
            return matches[0]

    return None


def updated_note_from_filter(notes_list, search_string: str, current_note: str):
    matching_note = find_matching_note(notes_list, search_string)
    # don't update if the note already matches the filter to prevent infinite loop (where note update triggers filter
    # update which triggers note update and so on)
    if matching_note is not None and not matching_note[0] == current_note:
        return matching_note[0]


def note_search_updated_function(note_attribute, note_search_attribute, get_notes_list):
    def note_search_updated(data, context):
        notes_list = get_notes_list(data, context)
        matching_note = updated_note_from_filter(notes_list,
                                                 getattr(data, note_search_attribute),
                                                 getattr(data, note_attribute))

        if matching_note is not None:
            setattr(data, note_attribute, matching_note)

    return lambda data, context: note_search_updated(data, context)


def dynamic_enum_default(default: int):
    # Blender versions before 2.90 don't support defaults on dynamic enums
    return default if blender_version >= (2, 90, 0) else None


def note_property(name: str, description: str, get_notes_list, note_attribute: str, note_search_attribute: str,
                  default_pitch=0):
    """
    :param name: note property name
    :param description: note property description
    :param get_notes_list: function to get list of note enums
    :param note_attribute: note property attribute
    :param note_search_attribute: note search property attribute
    :param default_pitch: default pitch for property
    :return:
    """
    return EnumProperty(items=get_notes_list, name=name, description=description,
                        default=dynamic_enum_default(default_pitch),
                        update=note_updated_function(note_attribute, note_search_attribute, get_notes_list))


def note_search_property(note_attribute, note_search_attribute, get_notes_list):
    return StringProperty(name=i18n.get_key(i18n.SEARCH), description=i18n.get_key(i18n.NOTE_SEARCH_DESCRIPTION),
                          update=note_search_updated_function(note_attribute, note_search_attribute, get_notes_list))


NO_SELECTION = "[No Selection]"
