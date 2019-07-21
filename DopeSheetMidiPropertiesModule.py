if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
else:
    from . import midi_data

    from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, PointerProperty, CollectionProperty, \
        FloatProperty
    from bpy.types import PropertyGroup


def get_midi_file_name(self):
    if "midi_file" in self:
        return self["midi_file"]
    return ""


def get_notes_list(self, context):
    return midi_data.dope_sheet_midi_data.get_notes_list(self, context)


def get_tracks_list(self, context):
    return midi_data.dope_sheet_midi_data.get_tracks_list(self, context)


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


class DopeSheetMidiPropertyGroup(PropertyGroup):
    midi_file: StringProperty(name="Midi File", description="Select Midi File", get=get_midi_file_name)
    notes_list: EnumProperty(items=get_notes_list,
                             name="Note",
                             description="Note")
    track_list: EnumProperty(items=get_tracks_list,
                             name="Track",
                             description="Selected Midi Track")

    dope_sheet_note_action_property: PointerProperty(type=DopeSheetNoteActionProperty)
    midi_frame_start: \
        IntProperty(name="First Frame",
                    description="The frame corresponding to the beginning of the midi file",
                    default=1)
