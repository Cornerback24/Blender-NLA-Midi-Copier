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
# noinspection PyUnresolvedReferences
import addon_utils
import traceback
from bpy.props import PointerProperty
from bpy.types import NlaStrip
from .NLAMidiCopierModule import NLA_MIDI_COPIER_OT_copier, NLA_MIDI_COPIER_OT_instrument_copier, \
    NLA_MIDI_COPIER_OT_all_instrument_copier, NLA_MIDI_COPIER_OT_bulk_midi_copier
from .DopeSheetMidiCopierModule import NLA_MIDI_COPIER_PT_dope_sheet_copier
from .GraphEditorKeyframeGeneratorModule import NLA_MIDI_COPIER_OT_graph_editor_keyframe_generator, \
    NLA_MIDI_COPIER_OT_load_min_max_from_midi_track
from .MidiInstrumentModule import NLA_MIDI_COPIER_OT_add_instrument, NLA_MIDI_COPIER_OT_delete_instrument, \
    NLA_MIDI_COPIER_OT_add_action_to_instrument, NLA_MIDI_COPIER_OT_remove_action_from_instrument, \
    NLA_MIDI_COPIER_OT_transpose_instrument
from .OperatorUtils import NLA_MIDI_COPIER_OT_copy_midi_file_data
from .PanelUtils import MidiFileSelector
from .OtherToolsModule import NLA_MIDI_COPIER_OT_generate_transitions_operator, \
    NLA_MIDI_COPIER_OT_delete_transitions_operator
from .MidiPanelModule import NLA_MIDI_COPIER_PT_midi_panel, NLA_MIDI_COPIER_PT_midi_instrument_panel, \
    NLA_MIDI_COPIER_PT_quick_copy_panel, NLA_MIDI_COPIER_PT_midi_settings_panel, \
    NLA_MIDI_COPIER_PT_other_tools_panel, MIDI_TRACK_PROPERTIES_UL_list
from .GraphEditorMidiPanelModule import NLA_MIDI_COPIER_PT_graph_editor_midi_panel, \
    NLA_MIDI_COPIER_PT_graph_editor_midi_settings_panel
from .DopeSheetMidiPanelModule import NLA_MIDI_COPIER_PT_dope_sheet_midi_panel, \
    NLA_MIDI_COPIER_PT_dope_sheet_midi_settings_panel
from .MidiPropertiesModule import MidiTrackProperty, MidiPropertyGroup, NoteActionProperty, InstrumentNoteProperty, \
    InstrumentProperty, NoteFilterGroup, NoteFilterProperty, \
    GenericNoteFilterProperty, GenericNoteFilterGroup, NoteFilterPreset, \
    BulkCopyPropertyGroup, TempoPropertyGroup, \
    MidiCopierVersion, MidiDataCommon, KeyframeProperties, OtherToolsPropertyGroup
from .DopeSheetMidiPropertiesModule import DopeSheetMidiPropertyGroup, DopeSheetNoteActionProperty, \
    DopeSheetNoteFilterProperty, DopeSheetNoteFilterGroup, DopeSheetTempoPropertyGroup
from .GraphEditorMidiPropertiesModule import GraphEditorTempoPropertyGroup, GraphEditorNoteActionProperty, \
    GraphEditorNoteFilterProperty, GraphEditorNoteFilterGroup, GraphEditorMidiPropertyGroup, \
    GraphEditorKeyframeGenerationProperty
from .NoteFilterModule import NLA_MIDI_COPIER_OT_add_note_filter, NLA_MIDI_COPIER_OT_remove_note_filter, \
    NLA_MIDI_COPIER_OT_add_note_filter_group, NLA_MIDI_COPIER_OT_remove_note_filter_group, \
    NLA_MIDI_COPIER_OT_reorder_note_filter, \
    NLA_MIDI_COPIER_OT_add_note_filter_preset, NLA_MIDI_COPIER_OT_save_note_filter_preset, \
    NLA_MIDI_COPIER_OT_delete_note_filter_preset
from .midi_data import MidiDataType
from .i18n.es_strings import i18n_es
from .PreferenceModule import MidiCopierPreferences

classes = [
    NoteFilterProperty, NoteFilterGroup, GenericNoteFilterProperty, GenericNoteFilterGroup, NoteFilterPreset,
    BulkCopyPropertyGroup,
    NoteActionProperty, InstrumentNoteProperty, InstrumentProperty, NLA_MIDI_COPIER_OT_add_instrument,
    NLA_MIDI_COPIER_OT_delete_instrument, NLA_MIDI_COPIER_OT_copier,
    NLA_MIDI_COPIER_OT_instrument_copier, NLA_MIDI_COPIER_OT_all_instrument_copier, NLA_MIDI_COPIER_OT_bulk_midi_copier,
    NLA_MIDI_COPIER_OT_add_action_to_instrument, NLA_MIDI_COPIER_OT_remove_action_from_instrument,
    NLA_MIDI_COPIER_OT_transpose_instrument,
    NLA_MIDI_COPIER_OT_add_note_filter, NLA_MIDI_COPIER_OT_remove_note_filter, NLA_MIDI_COPIER_OT_add_note_filter_group,
    NLA_MIDI_COPIER_OT_remove_note_filter_group, NLA_MIDI_COPIER_OT_reorder_note_filter,
    NLA_MIDI_COPIER_OT_add_note_filter_preset, NLA_MIDI_COPIER_OT_save_note_filter_preset,
    NLA_MIDI_COPIER_OT_delete_note_filter_preset,
    NLA_MIDI_COPIER_OT_copy_midi_file_data,
    TempoPropertyGroup, MidiCopierVersion, MidiTrackProperty,
    KeyframeProperties, OtherToolsPropertyGroup, MidiPropertyGroup, MidiDataCommon,
    MIDI_TRACK_PROPERTIES_UL_list, NLA_MIDI_COPIER_PT_midi_panel, MidiFileSelector,
    NLA_MIDI_COPIER_OT_generate_transitions_operator, NLA_MIDI_COPIER_OT_delete_transitions_operator,
    NLA_MIDI_COPIER_PT_midi_instrument_panel, NLA_MIDI_COPIER_PT_quick_copy_panel,
    NLA_MIDI_COPIER_PT_midi_settings_panel, NLA_MIDI_COPIER_PT_other_tools_panel]
dope_sheet_classes = [DopeSheetNoteFilterProperty, DopeSheetNoteFilterGroup,
                      DopeSheetNoteActionProperty, DopeSheetTempoPropertyGroup,
                      NLA_MIDI_COPIER_PT_dope_sheet_copier, DopeSheetMidiPropertyGroup,
                      NLA_MIDI_COPIER_PT_dope_sheet_midi_panel,
                      NLA_MIDI_COPIER_PT_dope_sheet_midi_settings_panel]
graph_editor_classes = [GraphEditorNoteFilterProperty, GraphEditorNoteFilterGroup,
                        GraphEditorKeyframeGenerationProperty,
                        GraphEditorNoteActionProperty, GraphEditorTempoPropertyGroup,
                        NLA_MIDI_COPIER_OT_graph_editor_keyframe_generator, GraphEditorMidiPropertyGroup,
                        NLA_MIDI_COPIER_OT_load_min_max_from_midi_track,
                        NLA_MIDI_COPIER_PT_graph_editor_midi_panel, NLA_MIDI_COPIER_PT_graph_editor_midi_settings_panel]
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


def addon_version():
    for module in addon_utils.modules():
        if "name" in module.bl_info and \
                (module.bl_info["name"] == "NLA Midi Copier"
                 # support running compatibility updates from before rename to remove "Blender" from the name
                 or module.bl_info["name"] == "Blender NLA Midi Copier"):
            return module.bl_info["version"]
    return None


def updates_from_previous_version(context):
    version_property = context.scene.midi_copier_version
    current_version = addon_version()
    if current_version is not None:
        CompatibilityModule.run_compatibility_updates(current_version)
        version_property.major = current_version[0]
        version_property.minor = current_version[1]
        version_property.revision = current_version[2]


# noinspection PyArgumentList
def register():
    bpy.app.translations.register(__name__, translations)
    for clazz in classes:
        bpy.utils.register_class(clazz)
    bpy.types.Scene.midi_data_property = PointerProperty(type=MidiPropertyGroup)
    bpy.types.Scene.dope_sheet_midi_data_property = PointerProperty(type=DopeSheetMidiPropertyGroup)
    bpy.types.Scene.graph_editor_midi_data_property = PointerProperty(type=GraphEditorMidiPropertyGroup)
    bpy.types.Scene.midi_copier_version = PointerProperty(type=MidiCopierVersion)
    bpy.types.Scene.midi_copier_data_common = PointerProperty(type=MidiDataCommon)
    bpy.app.handlers.load_post.append(on_load)


def unregister():
    del bpy.types.Scene.midi_copier_version
    del bpy.types.Scene.graph_editor_midi_data_property
    del bpy.types.Scene.dope_sheet_midi_data_property
    del bpy.types.Scene.midi_data_property
    for clazz in reversed(classes):
        bpy.utils.unregister_class(clazz)
    bpy.app.translations.unregister(__name__)


if __name__ == "__main__":
    register()
