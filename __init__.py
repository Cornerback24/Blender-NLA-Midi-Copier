bl_info = \
    {
        "name": "Blender NLA Midi Copier",
        "author": "Cornerback24",
        "version": (0, 2, 0),
        "blender": (2, 80, 0),
        "location": "View NLA Editor > Tool Shelf",
        "description": "Copy actions to action strips based on midi file input",
        "wiki_url": "",
        "tracker_url": "",
        "category": "Animation",
    }

if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NLAMidiCopierModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiPanelModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiPropertiesModule)
else:
    # noinspection PyUnresolvedReferences
    from . import NLAMidiCopierModule
    # noinspection PyUnresolvedReferences
    from . import MidiPanelModule
    # noinspection PyUnresolvedReferences
    from . import MidiPropertiesModule

import bpy
from bpy.props import PointerProperty
from bpy.types import NlaStrip
from .NLAMidiCopierModule import NLAMidiCopier
from .MidiPanelModule import MidiPanel, OneClickMidiPanel
from .MidiPropertiesModule import MidiPropertyGroup, NoteActionProperty
from .MidiPanelModule import MidiFileSelector

classes = [NoteActionProperty, MidiPropertyGroup, MidiPanel, MidiFileSelector, NLAMidiCopier]


# noinspection PyArgumentList
def register():
    for clazz in classes:
        bpy.utils.register_class(clazz)
    bpy.types.Scene.midi_data_property = PointerProperty(type=MidiPropertyGroup)


def unregister():
    for clazz in classes:
        bpy.utils.unregister_class(clazz)
    del bpy.types.Scene.midi_data_property


if __name__ == "__main__":
    register()
