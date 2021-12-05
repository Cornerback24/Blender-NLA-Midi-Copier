if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiPropertiesModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PropertyUtils)
else:
    from . import midi_data
    from . import MidiPropertiesModule
    from . import NoteFilterImplementations
    from . import PropertyUtils

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


UNIT_TYPES = \
    {
        "NONE": ("None", "None", 0, "min_value", "max_value"),
        "ACCELERATION": ("Acceleration", "Acceleration", 1, "min_value_acceleration", "max_value_acceleration"),
        "ANGLE": ("Angle", "Angle", 2, "min_value_angle", "max_value_angle"),
        "AREA": ("Area", "Area", 3, "min_value_area", "max_value_area"),
        "LENGTH": ("Distance/Length", "Distance/Length", 4, "min_value_length", "max_value_length"),
        "MASS": ("Mass", "Mass", 5, "min_value_mass", "max_value_mass"),
        "POWER": ("Power", "Power", 6, "min_value_power", "max_value_power"),
        "TEMPERATURE": ("Temperature", "Temperature", 7, "min_value_temperature", "max_value_temperature"),
        "VELOCITY": ("Velocity", "Velocity", 8, "min_value_velocity", "max_value_velocity"),
        "VOLUME": ("Volume", "Volume", 9, "min_value_volume", "max_value_volume")
    }
if blender_version < (2, 92, 0):  # previous versions do not have this option for float property
    del UNIT_TYPES['TEMPERATURE']

unit_type_enums = [(key, value[0], value[1], value[2]) for key, value in UNIT_TYPES.items()]


def min_float_property(subtype='NONE', unit='NONE'):
    return FloatProperty(name="Min",
                         description="Minimum keyframe value to generate",
                         default=0, subtype=subtype, unit=unit)


def max_float_property(subtype='NONE', unit='NONE'):
    return FloatProperty(name="Max",
                         description="Maximum keyframe value to generate",
                         default=1, subtype=subtype, unit=unit)


NOTE_PROPERTIES = [("Pitch", "Pitch", "Pitch", 0),
                   ("Length", "Length (frames)", "Note Length in Frames", 1),
                   ("Velocity", "Velocity", "Velocity", 2)]

OVERLAP_OPTIONS = [("REPLACE", "Replace", "Replace existing keyframe if on the same frame", 0),
                   ("SKIP", "Skip", "Skip keyframe if an existing keyframe is on the same frame", 1),
                   ("PREVIOUS_FRAME", "Previous frame",
                    "If an existing keyframe is on the same frame, place the generated keyframe on "
                    "the frame before the existing keyframe. If the frame before also has a "
                    "keyframe, the generated keyframe will be skipped", 2),
                   ("NEXT_FRAME", "Next frame",
                    "If an existing keyframe is on the same frame, place the generated keyframe on "
                    "the frame after the existing keyframe. If the frame after also has a "
                    "keyframe, the generated keyframe will be skipped", 3)]

ON_NOTE_OVERLAP = [("include", "Include", "Generate keyframes for notes that overlap other notes", 0),
                   ("skip", "Skip",
                    "Skip notes if the first frame would be before the last frame of the previous note", 1)]


class GraphEditorKeyframeGenerationProperty(PropertyGroup):
    note_property: EnumProperty(items=NOTE_PROPERTIES, name="Note Property", default="Pitch")
    non_negative_min: FloatProperty(name="Map to min",
                                    description="Value from midi file to map to minimum keyframe value", min=0.0)
    non_negative_max: FloatProperty(name="Map to max",
                                    description="Value from midi file to map to maximum keyframe value", min=0.0,
                                    default=1.0)
    int_0_to_127_min: IntProperty(name="Map to min",
                                  description="Value from midi file to map to minimum keyframe value",
                                  min=0, max=127)
    int_0_to_127_max: IntProperty(name="Map to max",
                                  description="Value from midi file to map to maximum keyframe value", min=0, max=127,
                                  default=127)
    pitch_min: PropertyUtils.note_property("Min note", "Lowest Note", get_all_notes, "pitch_min",
                                           "pitch_min_search_string")
    pitch_min_search_string: PropertyUtils.note_search_property("pitch_min", "pitch_min_search_string", get_all_notes)
    pitch_max: PropertyUtils.note_property("Max Note", "Highest note", get_all_notes, "pitch_max",
                                           "pitch_max_search_string", 127)
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
    unit_type: EnumProperty(items=unit_type_enums, name="Unit Type", default="NONE")
    on_keyframe_overlap: EnumProperty(items=OVERLAP_OPTIONS, name="Keyframe Overlap",
                                      description="Keyframe overlap handling mode")
    generate_at_note_end: \
        BoolProperty(name="Generate at Note End",
                     description="Generate keyframes at the end of the note instead of the beginning",
                     default=False)
    on_note_overlap: EnumProperty(name="Note overlap", items=ON_NOTE_OVERLAP)
    scale_filter_type: EnumProperty(items=MidiPropertiesModule.scale_filter_options, name="Filter by Scale",
                                    description="Filter by Scale")
    scale_filter_scale: EnumProperty(items=MidiPropertiesModule.scale_options, name="Scale", description="Major Scale")
    only_notes_in_selected_track: BoolProperty(name="Only Notes in Selected Track",
                                               description="Only calculate keyframes based on notes in the selected "
                                                           "track",
                                               default=False)


class GraphEditorNoteActionProperty(PropertyGroup, NoteActionPropertyBase):
    data_type = MidiDataType.GRAPH_EDITOR
    note_filter_groups: CollectionProperty(type=GraphEditorNoteFilterGroup, name="Note Filter Groups")
    keyframe_generators: CollectionProperty(type=GraphEditorKeyframeGenerationProperty, name="Note Filter Groups")
    delete_existing_keyframes: BoolProperty(name="Delete existing keyframes", description="Delete existing keyframes")


class GraphEditorTempoPropertyGroup(PropertyGroup, TempoPropertyBase):
    data_type = MidiDataType.GRAPH_EDITOR


class GraphEditorMidiPropertyGroup(MidiPropertyBase, PropertyGroup):
    data_type = MidiDataType.GRAPH_EDITOR
    note_action_property: PointerProperty(type=GraphEditorNoteActionProperty)
    tempo_settings: PointerProperty(type=GraphEditorTempoPropertyGroup)
