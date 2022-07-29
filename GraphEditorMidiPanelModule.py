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
from .GraphEditorKeyframeGeneratorModule import GraphEditorMidiKeyframeGenerator, LoadMinMaxFromMidiTrack


class GraphEditorMidiPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_category = "Midi"
    bl_label = "Graph Editor Midi"
    bl_idname = "ANIMATION_PT_graph_editor_midi_panel"

    def draw(self, context):
        midi_data_property = context.scene.graph_editor_midi_data_property
        midi_file = midi_data_property.midi_file
        graph_editor_note_action_property = midi_data_property.note_action_property
        col = self.layout.column(align=True)

        if len(graph_editor_note_action_property.keyframe_generators) == 0:
            # This should only happen in the case that the add-on was updated from a previous version while
            # the blend file was open (since the one GraphEditorKeyframeGenerationProperty is added in on_load)
            col.label(text="Reload the blend file to see options here.")
            return

        # only one keyframe generator for now
        keyframe_generator = graph_editor_note_action_property.keyframe_generators[0]

        # only one keyframe generator for now
        draw_notes_in_track_label = keyframe_generator.note_property == "Pitch"
        PanelUtils.draw_midi_file_selections(
            col, midi_data_property, MidiDataType.GRAPH_EDITOR, context,
            note_property_text="Notes in Track:" if draw_notes_in_track_label else "Note:")

        left, right, data_path_row = PanelUtils.split_row(col, .2)
        right.enabled = False
        fcurves = context.selected_editable_fcurves
        if len(fcurves) == 1:
            # label instead of text argument so that label is not greyed out
            left.label(text="Selected F-Curve:")
            right.prop(fcurves[0], "data_path", text="")
        elif len(fcurves) > 1:
            left.label(text="Selected F-Curves:")
            selected_fcuves_column = right.column(align=True)
            for fcurve in fcurves[0:4]:  # only draw first four
                selected_fcuves_column.prop(fcurve, "data_path", text="")
            if len(fcurves) > 4:
                selected_fcuves_column.label(text="...")
        else:
            left.label(text="Selected F-Curve:")
            right.label(text="No F-Curve selected")

        col.separator()
        col = self.layout.column(align=True)
        left, right, row = PanelUtils.split_row(col, .2)
        left.label(text="Note Property:")
        right.prop(keyframe_generator, "note_property", text="")
        operator_row = right.row()
        operator_row.enabled = midi_file is not None and len(midi_file) > 0
        operator_row.operator(LoadMinMaxFromMidiTrack.bl_idname, text="", icon='IMPORT')
        if keyframe_generator.note_property == "Pitch":
            self.draw_pitch(col, keyframe_generator)
        else:
            self.draw_min_and_max(col, keyframe_generator)

        min_max_row = col.row()
        min_max_row.prop(keyframe_generator,
                         GraphEditorMidiPropertiesModule.UNIT_TYPES[keyframe_generator.unit_type][3])
        min_max_row.prop(keyframe_generator,
                         GraphEditorMidiPropertiesModule.UNIT_TYPES[keyframe_generator.unit_type][4])
        PanelUtils.indented_row(col).prop(keyframe_generator, "unit_type")

        col.separator()
        col = self.layout.column(align=True)
        col.prop(keyframe_generator, "generate_at_note_end")
        col.prop(graph_editor_note_action_property, "add_filters")
        if graph_editor_note_action_property.add_filters:
            PanelUtils.draw_filter_box(col, graph_editor_note_action_property, False, None,
                                       MidiDataType.GRAPH_EDITOR)
        col.prop(keyframe_generator, "on_keyframe_overlap")
        col.prop(keyframe_generator, "on_note_overlap")
        col.prop(midi_data_property, "midi_frame_start")
        col.prop(graph_editor_note_action_property, "midi_frame_offset")
        col.separator()
        col = self.layout.column(align=True)

        tooltip_creator = PanelUtils.OperatorTooltipCreator(GraphEditorMidiKeyframeGenerator)

        if midi_file is None or len(midi_file) == 0:
            tooltip_creator.add_disable_description("No midi file selected")
        if midi_file is not None and len(midi_file) > 0 and len(fcurves) == 0:
            tooltip_creator.add_disable_description("Select an F-Curve in the Graph Editor")

        tooltip_creator.draw_operator_row(col, icon='FILE_SOUND')

    def draw_min_and_max(self, col, keyframe_generator):
        min_max_map_row = col.row()
        note_property = keyframe_generator.note_property
        min_max_map_row.prop(keyframe_generator,
                             GraphEditorKeyframeGeneratorModule.note_property_definitions[note_property][1])
        min_max_map_row.prop(keyframe_generator,
                             GraphEditorKeyframeGeneratorModule.note_property_definitions[note_property][2])

    def draw_pitch(self, col, keyframe_generator):
        PanelUtils.draw_note_with_search(col, keyframe_generator, "pitch_min", "pitch_min_search_string",
                                         text="Min note:")
        PanelUtils.draw_note_with_search(col, keyframe_generator, "pitch_max", "pitch_max_search_string",
                                         text="Max note:")
        box = PanelUtils.indented_row(col).box()
        PanelUtils.draw_scale_filter(box, keyframe_generator, "scale_filter_type", "scale_filter_scale")
        box.prop(keyframe_generator, "only_notes_in_selected_track")


class GraphEditorMidiSettingsPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_category = "Midi"
    bl_label = "Midi Settings"
    bl_idname = "ANIMATION_PT_graph_editor_midi_settings_panel"

    def draw(self, context):
        PanelUtils.draw_common_midi_settings(self.layout, context, MidiDataType.GRAPH_EDITOR)
