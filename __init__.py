bl_info = \
    {
        "name": "Blender NLA Midi Copier",
        "author": "Cornerback24",
        "version": (0, 7, 0),
        "blender": (2, 80, 0),
        "location": "View NLA Editor > Tool Shelf",
        "description": "Copy actions to action strips based on midi file input",
        "wiki_url": "https://github.com/Cornerback24/Blender-NLA-Midi-Copier#blender-nla-midi-copier",
        "tracker_url": "https://github.com/Cornerback24/Blender-NLA-Midi-Copier/issues",
        "support": "COMMUNITY",
        "category": "Animation"
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
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterModule)
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
    # noinspection PyUnresolvedReferences
    from . import NoteFilterModule

import bpy
from bpy.props import PointerProperty
from bpy.types import NlaStrip
from .NLAMidiCopierModule import NLAMidiCopier, NLAMidiInstrumentCopier, NLAMidiAllInstrumentCopier
from .DopeSheetMidiCopierModule import DopeSheetMidiCopier
from .MidiInstrumentModule import AddInstrument, DeleteInstrument, AddActionToInstrument, RemoveActionFromInstrument, \
    TransposeInstrument, CopyMidiPanelActionToInstrument
from .MidiPanelModule import MidiPanel, MidiInstrumentPanel, CopyToInstrumentPanel, MidiSettingsPanel
from .DopeSheetMidiPanelModule import DopeSheetMidiPanel, DopeSheetMidiSettingsPanel
from .MidiPropertiesModule import MidiPropertyGroup, NoteActionProperty, InstrumentNoteProperty, InstrumentProperty, \
    NoteFilterGroup, NoteFilterProperty
from .DopeSheetMidiPropertiesModule import DopeSheetMidiPropertyGroup, DopeSheetNoteActionProperty, \
    DopeSheetNoteFilterProperty, DopeSheetNoteFilterGroup
from .MidiPanelModule import MidiFileSelector
from .DopeSheetMidiPanelModule import DopeSheetMidiFileSelector
from .NoteFilterModule import AddNoteFilter, RemoveNoteFilter, AddNoteFilterGroup, RemoveFilterGroup, ReorderFilter

classes = [
    NoteFilterProperty, NoteFilterGroup,
    DopeSheetNoteFilterProperty, DopeSheetNoteFilterGroup,
    NoteActionProperty, InstrumentNoteProperty, InstrumentProperty,
    AddInstrument, DeleteInstrument, NLAMidiCopier, NLAMidiInstrumentCopier, NLAMidiAllInstrumentCopier,
    AddActionToInstrument, RemoveActionFromInstrument, TransposeInstrument, CopyMidiPanelActionToInstrument,
    AddNoteFilter, RemoveNoteFilter, AddNoteFilterGroup, RemoveFilterGroup, ReorderFilter,
    MidiPropertyGroup, MidiPanel, MidiFileSelector, MidiInstrumentPanel, CopyToInstrumentPanel, MidiSettingsPanel,
    DopeSheetNoteActionProperty,
    DopeSheetMidiFileSelector, DopeSheetMidiCopier, DopeSheetMidiPropertyGroup, DopeSheetMidiPanel,
    DopeSheetMidiSettingsPanel]


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
