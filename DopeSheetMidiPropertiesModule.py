if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiPropertiesModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
else:
    from . import midi_data
    from . import MidiPropertiesModule
    from . import NoteFilterImplementations

from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, PointerProperty, CollectionProperty, \
    FloatProperty
from bpy.types import PropertyGroup


def get_midi_file_name(self):
    if "midi_file" in self:
        return self["midi_file"]
    return ""


def get_all_notes(self, context):
    return midi_data.dope_sheet_midi_data.get_all_notes(context)


def get_notes_list(self, context):
    return midi_data.dope_sheet_midi_data.get_notes_list(self, context)


def get_tracks_list(self, context):
    return midi_data.dope_sheet_midi_data.get_tracks_list(self, context)


class DopeSheetNoteFilterProperty(PropertyGroup):
    filter_type: EnumProperty(items=NoteFilterImplementations.FILTER_ENUM_PROPERTY_ITEMS, name="Filter Type",
                              description="Filter Type", default="note_pitch_filter")
    comparison_operator: EnumProperty(items=MidiPropertiesModule.COMPARISON_ENUM_PROPERTY_ITEMS,
                                      name="Comparison Operator",
                                      description="Comparison Operator", default="equal_to")
    note_pitch: EnumProperty(items=get_all_notes, name="Pitch", description="Pitch")
    non_negative_int: IntProperty(name="Non Negative Int", description="Non-negative integer", min=0)
    positive_int: IntProperty(name="Positive Int", description="Positive Integer", min=1, default=1)
    positive_int_2: IntProperty(name="Positive Int", description="Positive Integer", min=1, default=1)
    int_0_to_127: IntProperty(name="Integer", description="Integer between 0 and 127, inclusive", min=0, max=127)
    non_negative_number: FloatProperty(name="Non negative number", description="Non negative number", min=0.0)
    time_unit: EnumProperty(items=MidiPropertiesModule.TIME_UNITS, name="Time unit", description="Time unit",
                            default="frames")


class DopeSheetNoteFilterGroup(PropertyGroup):
    note_filters: CollectionProperty(type=DopeSheetNoteFilterProperty, name="Note Filters")
    expanded: BoolProperty(name="Expanded", default=True)


class DopeSheetNoteActionProperty(PropertyGroup):
    midi_frame_offset: \
        IntProperty(name="Frame Offset",
                    description="Frame offset when copying strips")
    delete_source_keyframes: \
        BoolProperty(name="Delete Source Keyframes",
                     description="Delete the source keyframes after copying",
                     default=False)
    skip_overlaps: \
        BoolProperty(name="Skip Overlaps",
                     description="Skip notes if the first frame would be at or "
                                 "before the last frame of the previous note",
                     default=False)

    sync_length_with_notes: \
        BoolProperty(name="Sync Length with Notes",
                     description="Scale the copied keyframes' spacing so that the length matches the "
                                 "lengths of the notes they are copied to",
                     default=False)

    scale_factor: \
        FloatProperty(name="Scale Factor",
                      description="Scale factor for scaling to the note's length. "
                                  "For example, a scale factor of 1 will scale to the note's length, "
                                  "a scale factor of 2 will scale to twice the note's length, " +
                                  "and a scale factor of 0.5 will scale to half the note's length",
                      min=0.0000001, max=1000000, soft_min=0.0000001, soft_max=1000000, default=1)

    add_filters: \
        BoolProperty(name="Add filters",
                     description="Add filters to exclude notes",
                     default=False)

    filters_expanded: BoolProperty(name="Expanded", default=True)

    note_filter_groups: CollectionProperty(type=DopeSheetNoteFilterGroup, name="Note Filter Groups")


def update_middle_c(self, context):
    midi_data.dope_sheet_midi_data.middle_c_id = self.middle_c_note


class DopeSheetMidiPropertyGroup(PropertyGroup):
    midi_file: StringProperty(name="Midi File", description="Select Midi File", get=get_midi_file_name)
    notes_list: EnumProperty(items=get_notes_list,
                             name="Note",
                             description="Note")
    track_list: EnumProperty(items=get_tracks_list,
                             name="Track",
                             description="Selected Midi Track")

    note_action_property: PointerProperty(type=DopeSheetNoteActionProperty)
    midi_frame_start: \
        IntProperty(name="First Frame",
                    description="The frame corresponding to the beginning of the midi file",
                    default=1)

    middle_c_note: EnumProperty(items=MidiPropertiesModule.middle_c_options,
                                name="Middle C", description="The note corresponding to middle C (midi note 60)",
                                default="C4", update=update_middle_c)
