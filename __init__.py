bl_info = \
    {
        "name": "Blender NLA Midi Copier",
        "author": "Cornerback24",
        "version": (0, 1, 0),
        "blender": (2, 80, 0),
        "location": "View NLA Editor > Tool Shelf",
        "description": "Copy action strips based on midi file input",
        "warning": "Alpha release",
        "wiki_url": "",
        "tracker_url": "",
        "category": "Animation",
    }

if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NLAMidiCopierModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiPanelModule)
else:
    from . import midi_data
    # noinspection PyUnresolvedReferences
    from . import NLAMidiCopierModule
    # noinspection PyUnresolvedReferences
    from . import MidiPanelModule

import bpy
from bpy.props import EnumProperty, StringProperty, BoolProperty, IntProperty
from .NLAMidiCopierModule import NLAMidiCopier
from .MidiPanelModule import MidiPanel
from .MidiPanelModule import MidiFileSelector

classes = [MidiPanel, MidiFileSelector, NLAMidiCopier]


def get_tracks_list(self, context):
    return midi_data.get_tracks_list(self, context)


def get_notes_list(self, context):
    return midi_data.get_notes_list(self, context)


# noinspection PyArgumentList
def register():
    for clazz in classes:
        bpy.utils.register_class(clazz)
    # bpy.utils.register_class(MidiPanel)
    bpy.types.Scene.midi_linked_duplicate_property = \
        BoolProperty(name="Linked Duplicate",
                     description="Linked duplicate when copying NLA-Strips",
                     default=False)
    bpy.types.Scene.midi_file = StringProperty(name="Midi File", description="Select Midi File")
    bpy.types.Scene.notes_list = EnumProperty(items=get_notes_list,
                                              name="Note",
                                              description="Note")
    bpy.types.Scene.track_list = EnumProperty(items=get_tracks_list,
                                              name="Track",
                                              description="Selected Midi Track")
    bpy.types.Scene.midi_frame_start = \
        IntProperty(name="First Frame",
                    description="The frame corresponding to the beginning of the midi file",
                    default=1)
    bpy.types.Scene.midi_frame_offset = \
        IntProperty(name="Frame Offset",
                    description="Frame offset when copying strips")

    bpy.types.Scene.copy_to_new_track = \
        BoolProperty(name="Copy to New Track",
                     description="Place copied actions onto new tracks",
                     default=True)
    bpy.types.Scene.delete_source_action_strip = \
        BoolProperty(name="Delete Source Action",
                     description="Delete the source action after copying",
                     default=False)
    bpy.types.Scene.delete_source_track = \
        BoolProperty(name="Delete Source Track",
                     description="Delete the track containing the source action if it is empty",
                     default=False)


def unregister():
    for clazz in classes:
        bpy.utils.unregister_class(clazz)
    del bpy.types.Scene.midi_linked_duplicate_property
    del bpy.types.Scene.midi_file
    del bpy.types.Scene.notes_list
    del bpy.types.Scene.track_list
    del bpy.types.Scene.midi_frame_start
    del bpy.types.Scene.midi_frame_offset
    del bpy.types.Scene.copy_to_new_track
    del bpy.types.Scene.delete_source_action_strip
    del bpy.types.Scene.delete_source_track


if __name__ == "__main__":
    register()
