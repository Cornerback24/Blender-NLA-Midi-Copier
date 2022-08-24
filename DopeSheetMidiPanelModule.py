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
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from . import midi_data
    # noinspection PyUnresolvedReferences
    from . import DopeSheetMidiCopierModule
    # noinspection PyUnresolvedReferences
    from . import PanelUtils
    # noinspection PyUnresolvedReferences
    from . import MidiPanelModule
    from .i18n import i18n

import bpy
import textwrap
from .DopeSheetMidiCopierModule import DopeSheetMidiCopier
from . import midi_data
from bpy.props import EnumProperty
from .midi_data import MidiDataType


class DopeSheetMidiPanel(bpy.types.Panel):
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    bl_category = i18n.get_key(i18n.MIDI)
    bl_label = i18n.get_key(i18n.GREASE_PENCIL_MIDI)
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

        PanelUtils.draw_midi_file_selections(col, midi_data_property, MidiDataType.DOPESHEET, context)

        dope_sheet_note_action_property = midi_data_property.note_action_property

        self.layout.separator()
        col = self.layout.column(align=True)

        col.prop(dope_sheet_note_action_property, "delete_source_keyframes")
        col.prop(dope_sheet_note_action_property, "skip_overlaps")
        col.prop(dope_sheet_note_action_property, "sync_length_with_notes")
        col.prop(dope_sheet_note_action_property, "copy_to_note_end")
        col.prop(dope_sheet_note_action_property, "add_filters")

        if dope_sheet_note_action_property.add_filters:
            PanelUtils.draw_filter_box(col, dope_sheet_note_action_property, False, None,
                                       MidiDataType.DOPESHEET)

        col.prop(midi_data_property, "midi_frame_start")
        col.prop(dope_sheet_note_action_property, "midi_frame_offset")

        if dope_sheet_note_action_property.sync_length_with_notes:
            col.prop(dope_sheet_note_action_property, "scale_factor")

        self.layout.separator()
        col = self.layout.column(align=True)

        tooltip_creator = PanelUtils.OperatorTooltipCreator(DopeSheetMidiCopier)
        midi_file = midi_data_property.midi_file
        if midi_file is None or len(midi_file) == 0:
            tooltip_creator.add_disable_description(i18n.get_text_tip(i18n.NO_MIDI_FILE_SELECTED))
        tooltip_creator.draw_operator_row(col, icon='FILE_SOUND')


class DopeSheetMidiSettingsPanel(bpy.types.Panel):
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    bl_category = i18n.get_key(i18n.MIDI)
    bl_label = i18n.get_key(i18n.MIDI_SETTINGS)
    bl_idname = "ANIMATION_PT_dope_sheet_midi_settings_panel"

    @classmethod
    def poll(cls, context):
        return context.area.type == "DOPESHEET_EDITOR" and context.area.spaces[0].mode == "GPENCIL"

    def draw(self, context):
        PanelUtils.draw_common_midi_settings(self.layout, context, MidiDataType.DOPESHEET)

        dopesheet = context.area.spaces[0].dopesheet
        if not dopesheet.show_only_selected:
            col = self.layout.column(align=True)
            col.separator()
            col.label()
            only_selected_text = i18n.get_text(i18n.GREASE_PENCIL_ONLY_SELECTED)
            for line in textwrap.TextWrapper(width=35).wrap(text=only_selected_text):
                col.label(text=line)
