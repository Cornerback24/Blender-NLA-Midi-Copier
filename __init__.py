bl_info = \
    {
        "name": "Blender NLA Midi Copier",
        "author": "Cornerback24",
        "version": (0, 5, 1),
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
    importlib.reload(DopeSheetMidiPanelModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiPropertiesModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(DopeSheetMidiPropertiesModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiInstrumentModule)
else:
    # noinspection PyUnresolvedReferences
    from . import NLAMidiCopierModule
    # noinspection PyUnresolvedReferences
    from . import MidiPanelModule
    # noinspection PyUnresolvedReferences
    from . import MidiPropertiesModule
    # noinspection PyUnresolvedReferences
    from . import DopeSheetMidiPropertiesModule
    # noinspection PyUnresolvedReferences
    from . import MidiInstrumentModule

import bpy
from bpy.props import PointerProperty
from bpy.types import NlaStrip
from .NLAMidiCopierModule import NLAMidiCopier, NLAMidiInstrumentCopier, NLAMidiAllInstrumentCopier
from .DopeSheetMidiCopierModule import DopeSheetMidiCopier
from .MidiInstrumentModule import AddInstrument, DeleteInstrument, AddActionToInstrument, RemoveActionFromInstrument, \
    TransposeInstrument
from .MidiPanelModule import MidiPanel, MidiInstrumentPanel
from .DopeSheetMidiPanelModule import DopeSheetMidiPanel
from .MidiPropertiesModule import MidiPropertyGroup, NoteActionProperty, InstrumentNoteProperty, InstrumentProperty
from .DopeSheetMidiPropertiesModule import DopeSheetMidiPropertyGroup, DopeSheetNoteActionProperty
from .MidiPanelModule import MidiFileSelector
from .DopeSheetMidiPanelModule import DopeSheetMidiFileSelector

classes = [NoteActionProperty, InstrumentNoteProperty, InstrumentProperty,
           AddInstrument, DeleteInstrument, NLAMidiCopier, NLAMidiInstrumentCopier, NLAMidiAllInstrumentCopier,
           AddActionToInstrument, RemoveActionFromInstrument, TransposeInstrument,
           MidiPropertyGroup, MidiPanel, MidiFileSelector, MidiInstrumentPanel,
           DopeSheetNoteActionProperty,
           DopeSheetMidiFileSelector, DopeSheetMidiCopier, DopeSheetMidiPropertyGroup, DopeSheetMidiPanel]


# noinspection PyArgumentList
def register():
    for clazz in classes:
        bpy.utils.register_class(clazz)
    bpy.types.Scene.midi_data_property = PointerProperty(type=MidiPropertyGroup)
    bpy.types.Scene.dope_sheet_midi_data_property = PointerProperty(type=DopeSheetMidiPropertyGroup)


def unregister():
    for clazz in classes:
        bpy.utils.unregister_class(clazz)
    del bpy.types.Scene.midi_data_property


if __name__ == "__main__":
    register()
