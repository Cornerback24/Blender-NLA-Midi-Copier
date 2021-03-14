if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PanelUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiPanelModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(GraphEditorKeyframeGeneratorModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(GraphEditorMidiPropertiesModule)
else:
    from . import midi_data
    from . import PanelUtils
    from . import MidiPanelModule
    from . import GraphEditorKeyframeGeneratorModule
    from . import GraphEditorMidiPropertiesModule

import bpy
from .midi_data import MidiDataType
from .MidiPanelModule import MidiFileSelectorBase
from .GraphEditorKeyframeGeneratorModule import GraphEditorMidiKeyframeGenerator


class GraphEditorMidiFileSelector(MidiFileSelectorBase, bpy.types.Operator):
    data_type = MidiDataType.GRAPH_EDITOR
    bl_idname = "ops.graph_editor_midi_file_selector"


class GraphEditorMidiPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_category = "Midi"
    bl_label = "Graph Editor Midi"
    bl_idname = "ANIMATION_PT_graph_editor_midi_panel"

    def draw(self, context):
        midi_data_property = context.scene.graph_editor_midi_data_property
        midi_file = midi_data_property.midi_file

        col = self.layout.column(align=True)
        PanelUtils.draw_midi_file_selections(col, midi_data_property, GraphEditorMidiFileSelector.bl_idname,
                                             note_property_text="Notes in Track:")

        left, right, data_path_row = PanelUtils.split_row(col, .2)
        right.enabled = False
        left.label(text="Selected F-Curve:")
        if context.active_editable_fcurve is not None:
            right.prop(context.active_editable_fcurve, "data_path", text="")
        else:
            right.label(text="No F-Curve selected")

        graph_editor_note_action_property = midi_data_property.note_action_property

        if len(graph_editor_note_action_property.keyframe_generators) == 0:
            # This should only happen in the case that the add-on was updated from a previous version while
            # the blend file was open
            col.label(text="Reload the blend file to see options here.")
            return

        col.separator()
        col = self.layout.column(align=True)
        # only one keyframe generator for now
        keyframe_generator = graph_editor_note_action_property.keyframe_generators[0]
        PanelUtils.draw_note_with_search(col, keyframe_generator, "pitch_min", "pitch_min_search_string")
        PanelUtils.draw_note_with_search(col, keyframe_generator, "pitch_max", "pitch_max_search_string")
        box = PanelUtils.indented_row(col).box()
        PanelUtils.draw_scale_filter(box, keyframe_generator, "scale_filter_type", "scale_filter_scale")
        box.prop(keyframe_generator, "only_notes_in_selected_track")
        min_max_row = col.row()
        min_max_row.prop(keyframe_generator,
                         GraphEditorMidiPropertiesModule.UNIT_TYPES[keyframe_generator.unit_type][3])
        min_max_row.prop(keyframe_generator,
                         GraphEditorMidiPropertiesModule.UNIT_TYPES[keyframe_generator.unit_type][4])
        PanelUtils.indented_row(col).prop(keyframe_generator, "unit_type")

        col.separator()
        col = self.layout.column(align=True)
        col.prop(keyframe_generator, "generate_at_note_end")
        col.prop(keyframe_generator, "on_keyframe_overlap")
        col.prop(midi_data_property, "midi_frame_start")
        col.prop(graph_editor_note_action_property, "midi_frame_offset")
        col.separator()
        col = self.layout.column(align=True)

        generate_keyframes_button_row = col.row()
        generate_keyframes_button_row.enabled = midi_file is not None and len(midi_file) > 0 and \
                                                context.active_editable_fcurve is not None
        disabled_tooltip = None
        if midi_file is not None and context.active_editable_fcurve is None:
            disabled_tooltip = GraphEditorMidiKeyframeGenerator.bl_description + \
                               ".\n  ! Select an F-Curve in the Graph Editor"
        generate_keyframes_operator = \
            generate_keyframes_button_row.operator(GraphEditorMidiKeyframeGenerator.bl_idname, icon='FILE_SOUND')
        if disabled_tooltip is not None:
            generate_keyframes_operator.tooltip = disabled_tooltip


class GraphEditorMidiSettingsPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_category = "Midi"
    bl_label = "Midi Settings"
    bl_idname = "ANIMATION_PT_graph_editor_midi_settings_panel"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(context.scene.graph_editor_midi_data_property, "middle_c_note")
        col.separator()
        PanelUtils.draw_tempo_settings(col, context.scene.graph_editor_midi_data_property.tempo_settings)
