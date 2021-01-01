bl_info = \
    {
        "name": "Blender NLA Midi Copier",
        "author": "Cornerback24",
        "version": (0, 9, 2),
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
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
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
    # noinspection PyUnresolvedReferences
    from . import midi_data
    # noinspection PyUnresolvedReferences
    from bpy.app.handlers import persistent

import bpy
from bpy.props import PointerProperty
from bpy.types import NlaStrip
from .NLAMidiCopierModule import NLAMidiCopier, NLAMidiInstrumentCopier, NLAMidiAllInstrumentCopier, NLABulkMidiCopier
from .DopeSheetMidiCopierModule import DopeSheetMidiCopier
from .MidiInstrumentModule import AddInstrument, DeleteInstrument, AddActionToInstrument, RemoveActionFromInstrument, \
    TransposeInstrument
from .MidiPanelModule import MidiPanel, MidiInstrumentPanel, CopyToInstrumentPanel, MidiSettingsPanel
from .DopeSheetMidiPanelModule import DopeSheetMidiPanel, DopeSheetMidiSettingsPanel
from .MidiPropertiesModule import MidiPropertyGroup, NoteActionProperty, InstrumentNoteProperty, InstrumentProperty, \
    NoteFilterGroup, NoteFilterProperty, BulkCopyPropertyGroup, TempoPropertyGroup
from .DopeSheetMidiPropertiesModule import DopeSheetMidiPropertyGroup, DopeSheetNoteActionProperty, \
    DopeSheetNoteFilterProperty, DopeSheetNoteFilterGroup, DopeSheetTempoPropertyGroup
from .MidiPanelModule import MidiFileSelector
from .DopeSheetMidiPanelModule import DopeSheetMidiFileSelector
from .NoteFilterModule import AddNoteFilter, RemoveNoteFilter, AddNoteFilterGroup, RemoveFilterGroup, ReorderFilter

classes = [
    NoteFilterProperty, NoteFilterGroup,
    DopeSheetNoteFilterProperty, DopeSheetNoteFilterGroup, BulkCopyPropertyGroup,
    NoteActionProperty, InstrumentNoteProperty, InstrumentProperty, AddInstrument, DeleteInstrument, NLAMidiCopier,
    NLAMidiInstrumentCopier, NLAMidiAllInstrumentCopier, NLABulkMidiCopier,
    AddActionToInstrument, RemoveActionFromInstrument, TransposeInstrument,
    AddNoteFilter, RemoveNoteFilter, AddNoteFilterGroup, RemoveFilterGroup, ReorderFilter,
    TempoPropertyGroup,
    MidiPropertyGroup, MidiPanel, MidiFileSelector, MidiInstrumentPanel, CopyToInstrumentPanel, MidiSettingsPanel,
    DopeSheetNoteActionProperty, DopeSheetTempoPropertyGroup,
    DopeSheetMidiFileSelector, DopeSheetMidiCopier, DopeSheetMidiPropertyGroup, DopeSheetMidiPanel,
    DopeSheetMidiSettingsPanel]


def load_midi_file(midi_data_property, context):
    if midi_data_property.midi_file:
        try:
            midi_data.midi_data.update_midi_file(midi_data_property.midi_file, False, context)
        except Exception as e:
            print("Could not load midi file: " + str(e))
            midi_data.midi_data.update_midi_file(None, False, context)


@persistent
def on_load(scene):
    context = bpy.context
    load_midi_file(context.scene.midi_data_property, context)
    load_midi_file(context.scene.dope_sheet_midi_data_property, context)


# noinspection PyArgumentList
def register():
    for clazz in classes:
        bpy.utils.register_class(clazz)
    bpy.types.Scene.midi_data_property = PointerProperty(type=MidiPropertyGroup)
    bpy.types.Scene.dope_sheet_midi_data_property = PointerProperty(type=DopeSheetMidiPropertyGroup)
    bpy.app.handlers.load_post.append(on_load)


def unregister():
    for clazz in classes:
        bpy.utils.unregister_class(clazz)
    del bpy.types.Scene.midi_data_property


if __name__ == "__main__":
    register()
