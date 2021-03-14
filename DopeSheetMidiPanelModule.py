if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(DopeSheetMidiCopierModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PanelUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiPanelModule)
else:
    from . import midi_data
    # noinspection PyUnresolvedReferences
    from . import DopeSheetMidiCopierModule
    # noinspection PyUnresolvedReferences
    from . import PanelUtils
    # noinspection PyUnresolvedReferences
    from . import MidiPanelModule

import bpy
from .DopeSheetMidiCopierModule import DopeSheetMidiCopier
from . import midi_data
from bpy.props import EnumProperty
from .midi_data import MidiDataType
from .MidiPanelModule import MidiFileSelectorBase


class DopeSheetMidiFileSelector(MidiFileSelectorBase, bpy.types.Operator):
    data_type = MidiDataType.DOPESHEET
    bl_idname = "ops.dope_sheet_midi_file_selector"


class DopeSheetMidiPanel(bpy.types.Panel):
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    bl_category = "Midi"
    bl_label = "Grease Pencil Midi"
    bl_idname = "ANIMATION_PT_dope_sheet_midi_panel"

    @classmethod
    def poll(cls, context):
        if context.area.type == "DOPESHEET_EDITOR" and context.area.spaces[0].mode == "GPENCIL":
            dopesheet = context.area.spaces[0].dopesheet
            return dopesheet.show_only_selected
        return False

    def draw(self, context):
        col = self.layout.column(align=True)
        midi_data_property = context.scene.dope_sheet_midi_data_property

        PanelUtils.draw_midi_file_selections(col, midi_data_property, DopeSheetMidiFileSelector.bl_idname)

        dope_sheet_note_action_property = midi_data_property.note_action_property

        self.layout.separator()
        col = self.layout.column(align=True)

        col.prop(dope_sheet_note_action_property, "delete_source_keyframes")
        col.prop(dope_sheet_note_action_property, "skip_overlaps")
        col.prop(dope_sheet_note_action_property, "sync_length_with_notes")
        col.prop(dope_sheet_note_action_property, "copy_to_note_end")
        col.prop(dope_sheet_note_action_property, "add_filters")

        if dope_sheet_note_action_property.add_filters:
            PanelUtils.draw_filter_box(col, dope_sheet_note_action_property, False, None, "dope_sheet_midi_data")

        col.prop(midi_data_property, "midi_frame_start")
        col.prop(dope_sheet_note_action_property, "midi_frame_offset")

        if dope_sheet_note_action_property.sync_length_with_notes:
            col.prop(dope_sheet_note_action_property, "scale_factor")

        self.layout.separator()
        col = self.layout.column(align=True)

        col.operator(DopeSheetMidiCopier.bl_idname)


class DopeSheetMidiSettingsPanel(bpy.types.Panel):
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    bl_category = "Midi"
    bl_label = "Midi Settings"
    bl_idname = "ANIMATION_PT_dope_sheet_midi_settings_panel"

    @classmethod
    def poll(cls, context):
        return context.area.type == "DOPESHEET_EDITOR" and context.area.spaces[0].mode == "GPENCIL"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(context.scene.dope_sheet_midi_data_property, "middle_c_note")
        col.separator()
        PanelUtils.draw_tempo_settings(col, context.scene.dope_sheet_midi_data_property.tempo_settings)

        dopesheet = context.area.spaces[0].dopesheet
        if not dopesheet.show_only_selected:
            col.separator()
            col.label(text="Select \"Only Selected\"")
            col.label(text="in the Dope Sheet bar to show")
            col.label(text="the grease pencil midi panel.")
