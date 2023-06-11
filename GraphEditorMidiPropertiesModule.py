if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    # importlib.reload(MidiPropertiesModule) TODO something about this is causing script reload to fail
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PropertyUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from . import midi_data
    from . import MidiPropertiesModule
    from . import NoteFilterImplementations
    from . import PropertyUtils
    from .i18n import i18n

import bpy
from bpy.app import version as blender_version
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, PointerProperty, CollectionProperty, \
    FloatProperty
from bpy.types import PropertyGroup
from .midi_data import MidiDataType
from .MidiPropertiesModule import MidiPropertyBase, TempoPropertyBase, NoteActionPropertyBase, NoteFilterPropertyBase


class GraphEditorNoteFilterProperty(PropertyGroup, NoteFilterPropertyBase):
    data_type = MidiDataType.GRAPH_EDITOR


class GraphEditorNoteFilterGroup(PropertyGroup):
    note_filters: CollectionProperty(type=GraphEditorNoteFilterProperty, name="Note Filters")
    expanded: BoolProperty(name="Expanded", default=True)


def get_all_notes(keyframe_generation_property, context):
    return midi_data.get_midi_data(MidiDataType.GRAPH_EDITOR).get_all_notes_list()


def get_continuous_controllers(keyframe_generation_property, context):
    return midi_data.get_midi_data(MidiDataType.GRAPH_EDITOR).get_cc_data_list(context)


UNIT_TYPES = \
    {
        "NONE": (i18n.get_key(i18n.NONE), i18n.get_key(i18n.NONE), 0, "min_value", "max_value"),
        "ACCELERATION": (i18n.get_key(i18n.ACCELERATION),
                         i18n.get_key(i18n.ACCELERATION), 1, "min_value_acceleration", "max_value_acceleration"),
        "ANGLE": (i18n.get_key(i18n.ANGLE), i18n.get_key(i18n.ANGLE), 2, "min_value_angle", "max_value_angle"),
        "AREA": (i18n.get_key(i18n.AREA), i18n.get_key(i18n.AREA), 3, "min_value_area", "max_value_area"),
        "LENGTH": (i18n.get_key(i18n.DISTANCE_LENGTH), i18n.get_key(i18n.DISTANCE_LENGTH), 4, "min_value_length",
                   "max_value_length"),
        "MASS": (i18n.get_key(i18n.MASS), i18n.get_key(i18n.MASS), 5, "min_value_mass", "max_value_mass"),
        "POWER": (i18n.get_key(i18n.POWER), i18n.get_key(i18n.POWER), 6, "min_value_power", "max_value_power"),
        "TEMPERATURE": (i18n.get_key(i18n.TEMPERATURE),
                        i18n.get_key(i18n.TEMPERATURE), 7, "min_value_temperature", "max_value_temperature"),
        "VELOCITY": ("Velocity", i18n.get_key(i18n.VELOCITY), 8, "min_value_velocity", "max_value_velocity"),
        "VOLUME": ("Volume", i18n.get_key(i18n.VOLUME), 9, "min_value_volume", "max_value_volume")
    }
if blender_version < (2, 92, 0):  # previous versions do not have this option for float property
    del UNIT_TYPES['TEMPERATURE']

unit_type_enums = [(key, value[0], value[1], value[2]) for key, value in UNIT_TYPES.items()]


def min_float_property(subtype='NONE', unit='NONE'):
    return FloatProperty(name=i18n.get_key(i18n.MIN),
                         description=i18n.get_key(i18n.MINIMUM_KEYFRAME_VALUE_TO_GENERATE),
                         default=0, subtype=subtype, unit=unit)


def max_float_property(subtype='NONE', unit='NONE'):
    return FloatProperty(name=i18n.get_key(i18n.MAX),
                         description=i18n.get_key(i18n.MAXIMUM_KEYFRAME_VALUE_TO_GENERATE),
                         default=1, subtype=subtype, unit=unit)


NOTE_PROPERTIES = [("Pitch", i18n.get_key(i18n.PITCH), i18n.get_key(i18n.PITCH), 0),
                   ("Length", i18n.get_key(i18n.LENGTH_FRAMES), i18n.get_key(i18n.NOTE_LENGTH_IN_FRAMES), 1),
                   ("Velocity", i18n.get_key(i18n.VELOCITY), i18n.get_key(i18n.VELOCITY), 2)]

PROPERTY_TYPES = [("note", i18n.get_key(i18n.NOTE_PROPERTY), i18n.get_key(i18n.NOTE_PROPERTY), 0),
                  ("cc_data", i18n.get_key(i18n.CC_DATA), i18n.get_key(i18n.CC_DATA), 1)]

OVERLAP_OPTIONS = [("REPLACE", i18n.get_key(i18n.REPLACE), i18n.get_key(i18n.REPLACE_KEYFRAME_DESCRIPTION), 0),
                   ("SKIP", i18n.get_key(i18n.SKIP), i18n.get_key(i18n.SKIP_KEYFRAME_DESCRIPTION), 1),
                   ("PREVIOUS_FRAME", i18n.get_key(i18n.PREVIOUS_FRAME),
                    i18n.get_key(i18n.PREVIOUS_FRAME_DESCRIPTION), 2),
                   ("NEXT_FRAME", i18n.get_key(i18n.NEXT_FRAME), i18n.get_key(i18n.NEXT_FRAME_DESCRIPTION), 3)]

ON_NOTE_OVERLAP = [("include", i18n.get_key(i18n.INCLUDE),
                    i18n.get_key(i18n.NOTE_OVERLAP_INCLUDE_KEYFRAME_DESCRIPTION), 0),
                   ("skip", i18n.get_key(i18n.SKIP), i18n.get_key(i18n.NOTE_OVERLAP_SKIP_KEYFRAME_DESCRIPTION), 1)]

TRANSITION_PLACEMENT = [
    ("start", i18n.get_key(i18n.START), i18n.get_key(i18n.GRAPH_EDITOR_TRANSITION_START_DESCRIPTION), 0),
    ("end", i18n.get_key(i18n.END), i18n.get_key(i18n.GRAPH_EDITOR_TRANSITION_END_DESCRIPTION), 1)]


class GraphEditorKeyframeGenerationProperty(PropertyGroup):
    property_type: EnumProperty(items=PROPERTY_TYPES, name=i18n.get_key(i18n.PROPERTY_TYPE), default="note")
    note_property: EnumProperty(items=NOTE_PROPERTIES, name=i18n.get_key(i18n.NOTE_PROPERTY), default="Pitch")
    cc_type: EnumProperty(items=get_continuous_controllers, name=i18n.get_key(i18n.CC_TYPE))
    non_negative_min: FloatProperty(name=i18n.get_key(i18n.MAP_TO_MIN),
                                    description=i18n.get_key(i18n.MAP_TO_MIN_KEYFRAME_DESCRIPTION), min=0.0)
    non_negative_max: FloatProperty(name=i18n.get_key(i18n.MAP_TO_MAX),
                                    description=i18n.get_key(i18n.MAP_TO_MAX_KEYFRAME_DESCRIPTION), min=0.0,
                                    default=1.0)
    int_0_to_127_min: IntProperty(name=i18n.get_key(i18n.MAP_TO_MIN),
                                  description=i18n.get_key(i18n.MAP_TO_MIN_KEYFRAME_DESCRIPTION),
                                  min=0, max=127)
    int_0_to_127_max: IntProperty(name=i18n.get_key(i18n.MAP_TO_MAX),
                                  description=i18n.get_key(i18n.MAP_TO_MAX_KEYFRAME_DESCRIPTION), min=0, max=127,
                                  default=127)
    pitch_min: PropertyUtils.note_property(i18n.get_key(i18n.MIN_NOTE), i18n.get_key(i18n.LOWEST_NOTE), get_all_notes,
                                           "pitch_min", "pitch_min_search_string")
    pitch_min_search_string: PropertyUtils.note_search_property("pitch_min", "pitch_min_search_string", get_all_notes)
    pitch_max: PropertyUtils.note_property(i18n.get_key(i18n.MAX_NOTE), i18n.get_key(i18n.HIGHEST_NOTE), get_all_notes,
                                           "pitch_max", "pitch_max_search_string", 127)
    pitch_max_search_string: PropertyUtils.note_search_property("pitch_max", "pitch_max_search_string", get_all_notes)
    min_value: min_float_property()
    max_value: max_float_property()
    min_value_acceleration: min_float_property(unit='ACCELERATION')
    max_value_acceleration: max_float_property(unit='ACCELERATION')
    min_value_angle: min_float_property(subtype='ANGLE')
    max_value_angle: max_float_property(subtype='ANGLE')
    min_value_area: min_float_property(unit='AREA')
    max_value_area: max_float_property(unit='AREA')
    min_value_length: min_float_property(unit='LENGTH')
    max_value_length: max_float_property(unit='LENGTH')
    min_value_mass: min_float_property(unit='MASS')
    max_value_mass: max_float_property(unit='MASS')
    min_value_power: min_float_property(unit='POWER')
    max_value_power: max_float_property(unit='POWER')
    if blender_version >= (2, 92, 0):  # previous versions do not have this option for float property
        min_value_temperature: min_float_property(subtype='TEMPERATURE')
        max_value_temperature: max_float_property(subtype='TEMPERATURE')
    min_value_velocity: min_float_property(unit='VELOCITY')
    max_value_velocity: max_float_property(unit='VELOCITY')
    min_value_volume: min_float_property(unit='VOLUME')
    max_value_volume: max_float_property(unit='VOLUME')
    unit_type: EnumProperty(items=unit_type_enums, name=i18n.get_key(i18n.UNIT_TYPE), default="NONE")
    on_keyframe_overlap: EnumProperty(items=OVERLAP_OPTIONS, name=i18n.get_key(i18n.KEYFRAME_OVERLAP),
                                      description=i18n.get_key(i18n.KEYFRAME_OVERLAP_HANDLING_MODE))
    # keyframe placement properties
    keyframe_placement_note_start: BoolProperty(name=i18n.get_key(i18n.NOTE_START),
                                                description=i18n.get_key(i18n.NOTE_START),
                                                default=True)
    keyframe_placement_note_end: BoolProperty(name=i18n.get_key(i18n.NOTE_END),
                                              description=i18n.get_key(i18n.NOTE_END),
                                              default=False)
    keyframe_placement_cc_data_change: BoolProperty(name=i18n.get_key(i18n.ON_CC_CHANGE),
                                                    description=i18n.get_key(i18n.ON_CC_CHANGE),
                                                    default=False)

    on_note_overlap: EnumProperty(name=i18n.get_key(i18n.NOTE_OVERLAP), items=ON_NOTE_OVERLAP)
    limit_transition_length: BoolProperty(
        name=i18n.get_key(i18n.LIMIT_TRANSITION_LENGTH), default=False,
        description=i18n.get_key(i18n.GRAPH_EDITOR_LIMIT_TRANSITION_DESCRIPTION))
    transition_limit_frames: IntProperty(name=i18n.get_key(i18n.TRANSITION_LENGTH_FRAMES),
                                         description=i18n.get_key(i18n.GRAPH_EDITOR_TRANSITION_LENGTH_DESCRIPTION),
                                         default=10,
                                         min=1)
    transition_offset_frames: IntProperty(name=i18n.get_key(i18n.get_key(i18n.TRANSITION_OFFSET_FRAMES)),
                                          description=i18n.get_key(i18n.TRANSITION_OFFSET_FRAMES_DESCRIPTION),
                                          default=0,
                                          min=0)
    transition_placement: EnumProperty(items=TRANSITION_PLACEMENT, name=i18n.get_key(i18n.PLACEMENT),
                                       description=i18n.get_key(i18n.TRANSITION_PLACEMENT))
    scale_filter_type: EnumProperty(items=MidiPropertiesModule.scale_filter_options,
                                    name=i18n.get_key(i18n.FILTER_BY_SCALE),
                                    description=i18n.get_key(i18n.FILTER_BY_SCALE))
    scale_filter_scale: EnumProperty(items=MidiPropertiesModule.scale_options, name=i18n.get_key(i18n.SCALE),
                                     description=i18n.get_key(i18n.MAJOR_SCALE))
    only_notes_in_selected_track: BoolProperty(name=i18n.get_key(i18n.ONLY_NOTES_IN_SELECTED_TRACK),
                                               description=i18n.get_key(
                                                   i18n.ONLY_KEYFRAME_NOTES_IN_SELECTED_TRACK_DESCRIPTION),
                                               default=False)


class GraphEditorNoteActionProperty(PropertyGroup, NoteActionPropertyBase):
    data_type = MidiDataType.GRAPH_EDITOR
    note_filter_groups: CollectionProperty(type=GraphEditorNoteFilterGroup,
                                           name=i18n.get_key(i18n.ONLY_KEYFRAME_NOTES_IN_SELECTED_TRACK_DESCRIPTION))
    keyframe_generators: CollectionProperty(type=GraphEditorKeyframeGenerationProperty)
    delete_existing_keyframes: BoolProperty(name=i18n.get_key(i18n.DELETE_EXISTING_KEYFRAMES),
                                            description=i18n.get_key(i18n.DELETE_EXISTING_KEYFRAMES))


class GraphEditorTempoPropertyGroup(PropertyGroup, TempoPropertyBase):
    data_type = MidiDataType.GRAPH_EDITOR


class GraphEditorMidiPropertyGroup(MidiPropertyBase, PropertyGroup):
    data_type = MidiDataType.GRAPH_EDITOR
    note_action_property: PointerProperty(type=GraphEditorNoteActionProperty)
    tempo_settings: PointerProperty(type=GraphEditorTempoPropertyGroup)
