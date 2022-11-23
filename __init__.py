bl_info = \
    {
        "name": "Blender NLA Midi Copier",
        "author": "Cornerback24",
        "version": (0, 15, 1),
        "blender": (2, 80, 0),
        "location": "View NLA Editor > Tool Shelf",
        "description": "Copy actions to action strips based on midi file input",
        "doc_url": "https://github.com/Cornerback24/Blender-NLA-Midi-Copier#blender-nla-midi-copier",
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
    importlib.reload(GraphEditorKeyframeGeneratorModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(GraphEditorMidiPanelModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(DopeSheetMidiCopierModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(DopeSheetMidiPanelModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiPropertiesModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(DopeSheetMidiPropertiesModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(GraphEditorMidiPropertiesModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiInstrumentModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(CompatibilityModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PanelUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(OtherToolsModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(es_strings)
else:
    # noinspection PyUnresolvedReferences
    from . import NLAMidiCopierModule
    # noinspection PyUnresolvedReferences
    from . import MidiPanelModule
    # noinspection PyUnresolvedReferences
    from . import GraphEditorKeyframeGeneratorModule
    # noinspection PyUnresolvedReferences
    from . import GraphEditorMidiPanelModule
    # noinspection PyUnresolvedReferences
    from . import MidiPropertiesModule
    # noinspection PyUnresolvedReferences
    from . import DopeSheetMidiCopierModule
    # noinspection PyUnresolvedReferences
    from . import DopeSheetMidiPanelModule
    # noinspection PyUnresolvedReferences
    from . import DopeSheetMidiPropertiesModule
    # noinspection PyUnresolvedReferences
    from . import GraphEditorMidiPropertiesModule
    # noinspection PyUnresolvedReferences
    from . import MidiInstrumentModule
    # noinspection PyUnresolvedReferences
    from . import NoteFilterModule
    # noinspection PyUnresolvedReferences
    from . import midi_data
    # noinspection PyUnresolvedReferences
    from . import CompatibilityModule
    # noinspection PyUnresolvedReferences
    from . import PreferenceModule
    # noinspection PyUnresolvedReferences
    from . import PanelUtils
    # noinspection PyUnresolvedReferences
    from . import OtherToolsModule
    # noinspection PyUnresolvedReferences
    from bpy.app.handlers import persistent
    # noinspection PyUnresolvedReferences
    from .i18n import es_strings

import bpy
import traceback
from . import addon_updater_ops
from bpy.props import PointerProperty
from bpy.types import NlaStrip
from .NLAMidiCopierModule import NLAMidiCopier, NLAMidiInstrumentCopier, NLAMidiAllInstrumentCopier, NLABulkMidiCopier
from .DopeSheetMidiCopierModule import DopeSheetMidiCopier
from .GraphEditorKeyframeGeneratorModule import GraphEditorMidiKeyframeGenerator, LoadMinMaxFromMidiTrack
from .MidiInstrumentModule import AddInstrument, DeleteInstrument, AddActionToInstrument, RemoveActionFromInstrument, \
    TransposeInstrument
from .OperatorUtils import CopyMidiFileData
from .PanelUtils import MidiFileSelector
from .OtherToolsModule import GenerateTransitionsOperator, DeleteTransitionsOperator
from .MidiPanelModule import MidiPanel, MidiInstrumentPanel, QuickCopyPanel, MidiSettingsPanel, \
    OtherToolsPanel, MIDI_TRACK_PROPERTIES_UL_list
from .GraphEditorMidiPanelModule import GraphEditorMidiPanel, GraphEditorMidiSettingsPanel
from .DopeSheetMidiPanelModule import DopeSheetMidiPanel, DopeSheetMidiSettingsPanel
from .MidiPropertiesModule import MidiTrackProperty, MidiPropertyGroup, NoteActionProperty, InstrumentNoteProperty, \
    InstrumentProperty, NoteFilterGroup, NoteFilterProperty, BulkCopyPropertyGroup, TempoPropertyGroup, \
    MidiCopierVersion, KeyframeProperties, OtherToolsPropertyGroup
from .DopeSheetMidiPropertiesModule import DopeSheetMidiPropertyGroup, DopeSheetNoteActionProperty, \
    DopeSheetNoteFilterProperty, DopeSheetNoteFilterGroup, DopeSheetTempoPropertyGroup
from .GraphEditorMidiPropertiesModule import GraphEditorTempoPropertyGroup, GraphEditorNoteActionProperty, \
    GraphEditorNoteFilterProperty, GraphEditorNoteFilterGroup, GraphEditorMidiPropertyGroup, \
    GraphEditorKeyframeGenerationProperty
from .NoteFilterModule import AddNoteFilter, RemoveNoteFilter, AddNoteFilterGroup, RemoveFilterGroup, ReorderFilter
from .midi_data import MidiDataType
from .i18n.es_strings import i18n_es
from .PreferenceModule import MidiCopierPreferences

classes = [
    NoteFilterProperty, NoteFilterGroup, BulkCopyPropertyGroup,
    NoteActionProperty, InstrumentNoteProperty, InstrumentProperty, AddInstrument, DeleteInstrument, NLAMidiCopier,
    NLAMidiInstrumentCopier, NLAMidiAllInstrumentCopier, NLABulkMidiCopier,
    AddActionToInstrument, RemoveActionFromInstrument, TransposeInstrument,
    AddNoteFilter, RemoveNoteFilter, AddNoteFilterGroup, RemoveFilterGroup, ReorderFilter,
    CopyMidiFileData,
    TempoPropertyGroup, MidiCopierVersion, MidiTrackProperty,
    KeyframeProperties, OtherToolsPropertyGroup, MidiPropertyGroup,
    MIDI_TRACK_PROPERTIES_UL_list, MidiPanel, MidiFileSelector, GenerateTransitionsOperator, DeleteTransitionsOperator,
    MidiInstrumentPanel, QuickCopyPanel, MidiSettingsPanel, OtherToolsPanel]
dope_sheet_classes = [DopeSheetNoteFilterProperty, DopeSheetNoteFilterGroup,
                      DopeSheetNoteActionProperty, DopeSheetTempoPropertyGroup,
                      DopeSheetMidiCopier, DopeSheetMidiPropertyGroup, DopeSheetMidiPanel,
                      DopeSheetMidiSettingsPanel]
graph_editor_classes = [GraphEditorNoteFilterProperty, GraphEditorNoteFilterGroup,
                        GraphEditorKeyframeGenerationProperty,
                        GraphEditorNoteActionProperty, GraphEditorTempoPropertyGroup,
                        GraphEditorMidiKeyframeGenerator, GraphEditorMidiPropertyGroup,
                        LoadMinMaxFromMidiTrack,
                        GraphEditorMidiPanel, GraphEditorMidiSettingsPanel]
classes = classes + dope_sheet_classes + graph_editor_classes + [MidiCopierPreferences]


def create_i18n_dict(i18n_data):
    return {("*", key) if isinstance(key, str) else key: value for key, value in i18n_data.items() if value is not None}


translations = {'es': create_i18n_dict(i18n_es)}


def load_midi_file(midi_data_property, midi_data_type: int, context):
    if midi_data_property.midi_file:
        try:
            midi_data.get_midi_data(midi_data_type).update_midi_file(midi_data_property.midi_file, False, context)
        except Exception as e:
            print("Could not load midi file: " + str(e))
            print(traceback.format_exc())
            midi_data.get_midi_data(midi_data_type).update_midi_file(None, False, context)


@persistent
def on_load(scene):
    CompatibilityModule.compatibility_updates_complete = False
    context = bpy.context
    load_midi_file(context.scene.midi_data_property, MidiDataType.NLA, context)
    load_midi_file(context.scene.dope_sheet_midi_data_property, MidiDataType.DOPESHEET, context)
    load_midi_file(context.scene.graph_editor_midi_data_property, MidiDataType.GRAPH_EDITOR, context)

    # For now only one GraphEditorKeyframeGenerationProperty in the collection. Add it here to ensure it exists
    if len(context.scene.graph_editor_midi_data_property.note_action_property.keyframe_generators) == 0:
        context.scene.graph_editor_midi_data_property.note_action_property.keyframe_generators.add()
    updates_from_previous_version(context)
    CompatibilityModule.compatibility_updates_complete = True


def updates_from_previous_version(context):
    version_property = context.scene.midi_copier_version
    current_version = bl_info["version"]
    CompatibilityModule.run_compatibility_updates(current_version)
    version_property.major = current_version[0]
    version_property.minor = current_version[1]
    version_property.revision = current_version[2]


# noinspection PyArgumentList
def register():
    bpy.app.translations.register(__name__, translations)
    addon_updater_ops.register(bl_info)
    for clazz in classes:
        bpy.utils.register_class(clazz)
    bpy.types.Scene.midi_data_property = PointerProperty(type=MidiPropertyGroup)
    bpy.types.Scene.dope_sheet_midi_data_property = PointerProperty(type=DopeSheetMidiPropertyGroup)
    bpy.types.Scene.graph_editor_midi_data_property = PointerProperty(type=GraphEditorMidiPropertyGroup)
    bpy.types.Scene.midi_copier_version = PointerProperty(type=MidiCopierVersion)
    bpy.app.handlers.load_post.append(on_load)


def unregister():
    del bpy.types.Scene.midi_copier_version
    del bpy.types.Scene.graph_editor_midi_data_property
    del bpy.types.Scene.dope_sheet_midi_data_property
    del bpy.types.Scene.midi_data_property
    for clazz in reversed(classes):
        bpy.utils.unregister_class(clazz)
    addon_updater_ops.unregister()
    bpy.app.translations.unregister(__name__)


if __name__ == "__main__":
    register()
