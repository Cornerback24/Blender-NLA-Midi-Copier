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
