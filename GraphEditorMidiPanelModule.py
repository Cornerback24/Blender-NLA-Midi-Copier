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
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from . import midi_data
    from . import PanelUtils
    from . import MidiPanelModule
    from . import GraphEditorKeyframeGeneratorModule
    from . import GraphEditorMidiPropertiesModule
    from .i18n import i18n

import bpy
from . import addon_updater_ops
from .midi_data import MidiDataType
from .GraphEditorKeyframeGeneratorModule import GraphEditorMidiKeyframeGenerator, LoadMinMaxFromMidiTrack


class GraphEditorMidiPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_category = i18n.get_key(i18n.MIDI)
    bl_label = i18n.get_key(i18n.GRAPH_EDITOR_MIDI)
    bl_idname = "ANIMATION_PT_graph_editor_midi_panel"

    def draw(self, context):
        # Check for addon update in the background
        addon_updater_ops.check_for_update_background()

        midi_data_property = context.scene.graph_editor_midi_data_property
        midi_file = midi_data_property.midi_file
        graph_editor_note_action_property = midi_data_property.note_action_property
        col = self.layout.column(align=True)

        if len(graph_editor_note_action_property.keyframe_generators) == 0:
            # This should only happen in the case that the add-on was updated from a previous version while
            # the blend file was open (since the one GraphEditorKeyframeGenerationProperty is added in on_load)
            col.label(text=i18n.get_key(i18n.RELOAD_BLEND_FILE_FOR_OPTIONS))
            return

        # only one keyframe generator for now
        keyframe_generator = graph_editor_note_action_property.keyframe_generators[0]

        # only one keyframe generator for now
        draw_notes_in_track_label = keyframe_generator.note_property == "Pitch"
        PanelUtils.draw_midi_file_selections(
            col, midi_data_property, MidiDataType.GRAPH_EDITOR, context,
            note_property_text=i18n.get_label(i18n.NOTES_IN_TRACK) if draw_notes_in_track_label else i18n.get_label(
                i18n.NOTE))

        left, right, data_path_row = PanelUtils.split_row(col, .2)
        right.enabled = False
        fcurves = context.selected_editable_fcurves
        if len(fcurves) == 1:
            # label instead of text argument so that label is not greyed out
            left.label(text=i18n.get_label(i18n.SELECTED_F_CURVE))
            right.prop(fcurves[0], "data_path", text="")
        elif len(fcurves) > 1:
            left.label(text=i18n.get_label(i18n.SELECTED_F_CURVES))
            selected_fcuves_column = right.column(align=True)
            for fcurve in fcurves[0:4]:  # only draw first four
                selected_fcuves_column.prop(fcurve, "data_path", text="")
            if len(fcurves) > 4:
                selected_fcuves_column.label(text="...")
        else:
            left.label(text=i18n.get_label(i18n.SELECTED_F_CURVE))
            right.label(text=i18n.get_key(i18n.NO_F_CURVE_SELECTED))

        col.separator()
        col = self.layout.column(align=True)
        col.row().prop(keyframe_generator, "property_type", expand=True)

        left, right, row = PanelUtils.split_row(col, .2)
        if keyframe_generator.property_type == "cc_data":
            left.label(text=i18n.get_key(i18n.CC_TYPE))
            right.prop(keyframe_generator, "cc_type", text="")
        else:
            left.label(text=i18n.get_label(i18n.NOTE_PROPERTY))
            right.prop(keyframe_generator, "note_property", text="")
        operator_row = right.row()
        operator_row.enabled = midi_file is not None and len(midi_file) > 0
        operator_row.operator(LoadMinMaxFromMidiTrack.bl_idname, text="", icon='IMPORT')

        if keyframe_generator.property_type == "note" and keyframe_generator.note_property == "Pitch":
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
        col.label(text=i18n.get_label(i18n.KEYFRAME_PLACEMENT))
        row = PanelUtils.indented_row(col)
        row.prop(keyframe_generator, "keyframe_placement_note_start")
        row.prop(keyframe_generator, "keyframe_placement_note_end")
        if keyframe_generator.property_type == "cc_data":
            row.prop(keyframe_generator, "keyframe_placement_cc_data_change")
        col.prop(keyframe_generator, "on_keyframe_overlap")
        col.prop(keyframe_generator, "on_note_overlap")
        col.prop(keyframe_generator, "limit_transition_length")
        if keyframe_generator.limit_transition_length:
            PanelUtils.indented_row(col).prop(keyframe_generator, "transition_limit_frames")
            PanelUtils.indented_row(col).prop(keyframe_generator, "transition_offset_frames")
            PanelUtils.indented_row(col).prop(keyframe_generator, "transition_placement")
        col.prop(graph_editor_note_action_property, "add_filters")
        if graph_editor_note_action_property.add_filters:
            PanelUtils.draw_filter_box(col, graph_editor_note_action_property, False, None,
                                       MidiDataType.GRAPH_EDITOR)
        col.prop(midi_data_property, "midi_frame_start")
        col.prop(graph_editor_note_action_property, "midi_frame_offset")
        col.separator()
        col = self.layout.column(align=True)

        tooltip_creator = PanelUtils.OperatorTooltipCreator(GraphEditorMidiKeyframeGenerator)

        if midi_file is None or len(midi_file) == 0:
            tooltip_creator.add_disable_description(i18n.get_text_tip(i18n.NO_MIDI_FILE_SELECTED))
        if midi_file is not None and len(midi_file) > 0 and len(fcurves) == 0:
            tooltip_creator.add_disable_description(i18n.get_text_tip(i18n.SELECT_AN_F_CURVE_IN_THE_GRAPH_EDITOR))

        tooltip_creator.draw_operator_row(col, icon='FILE_SOUND')

        # notify update if available
        addon_updater_ops.update_notice_box_ui(self, context)

    def draw_min_and_max(self, col, keyframe_generator):
        min_max_map_row = col.row()
        if keyframe_generator.property_type == "cc_data":
            min_max_map_row.prop(keyframe_generator, "int_0_to_127_min")
            min_max_map_row.prop(keyframe_generator, "int_0_to_127_max")
        else:
            note_property = keyframe_generator.note_property
            min_max_map_row.prop(keyframe_generator,
                                 GraphEditorKeyframeGeneratorModule.note_property_definitions[note_property][1])
            min_max_map_row.prop(keyframe_generator,
                                 GraphEditorKeyframeGeneratorModule.note_property_definitions[note_property][2])

    def draw_pitch(self, col, keyframe_generator):
        PanelUtils.draw_note_with_search(col, keyframe_generator, "pitch_min", "pitch_min_search_string",
                                         text=i18n.get_label(i18n.MIN_NOTE))
        PanelUtils.draw_note_with_search(col, keyframe_generator, "pitch_max", "pitch_max_search_string",
                                         text=i18n.get_label(i18n.MAX_NOTE))
        box = PanelUtils.indented_row(col).box()
        PanelUtils.draw_scale_filter(box, keyframe_generator, "scale_filter_type", "scale_filter_scale")
        box.prop(keyframe_generator, "only_notes_in_selected_track")


class GraphEditorMidiSettingsPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_category = i18n.get_key(i18n.MIDI)
    bl_label = i18n.get_key(i18n.MIDI_SETTINGS)
    bl_idname = "ANIMATION_PT_graph_editor_midi_settings_panel"

    def draw(self, context):
        PanelUtils.draw_common_midi_settings(self.layout, context, MidiDataType.GRAPH_EDITOR)
