if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
else:
    from . import midi_data

    from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, PointerProperty, CollectionProperty
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
