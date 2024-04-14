if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NLAMidiCopierModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiInstrumentModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(OtherToolsModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PropertyUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PanelUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PitchUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(ActionUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from . import midi_data
    from . import NLAMidiCopierModule
    from . import MidiInstrumentModule
    from . import OtherToolsModule
    from . import PropertyUtils
    from . import PanelUtils
    from . import PitchUtils
    from . import ActionUtils
    from .i18n import i18n

import bpy
from typing import Callable, Tuple
from .NLAMidiCopierModule import NLAMidiCopier, NLAMidiInstrumentCopier, NLAMidiAllInstrumentCopier, NLABulkMidiCopier
from .MidiInstrumentModule import AddInstrument, DeleteInstrument, AddActionToInstrument, RemoveActionFromInstrument, \
    TransposeInstrument
from .OtherToolsModule import GenerateTransitionsOperator, DeleteTransitionsOperator
from . import midi_data
from bpy.props import EnumProperty
from .midi_data import MidiDataType


class MidiPanel(bpy.types.Panel):
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_category = i18n.get_key(i18n.MIDI)
    bl_label = i18n.get_key(i18n.NLA_MIDI)
    bl_idname = "ANIMATION_PT_midi_panel"

    def draw(self, context):
        col = self.layout.column(align=True)
        midi_data_property = context.scene.midi_data_property
        midi_file = midi_data_property.midi_file

        PanelUtils.draw_midi_file_selections(col, midi_data_property, MidiDataType.NLA, context)
        note_action_property = midi_data_property.note_action_property

        MidiPanel.draw_note_action_common(self.layout, col, note_action_property, context,
                                          midi_data_property=midi_data_property)

        self.layout.separator()

        col = self.layout.column(align=True)
        tooltip_creator = PanelUtils.OperatorTooltipCreator(NLAMidiCopier)
        if midi_file is None or len(midi_file) == 0:
            tooltip_creator.add_disable_description(i18n.get_text_tip(i18n.NO_MIDI_FILE_SELECTED))
        if note_action_property.action is None:
            tooltip_creator.add_disable_description(i18n.get_key(i18n.NO_ACTION_SELECTED))
        tooltip_creator.draw_operator_row(col, icon='FILE_SOUND')

    @staticmethod
    def draw_note_action_common(parent_layout, col, note_action_property, context, midi_data_property=None,
                                action_index=None):
        is_main_property = midi_data_property is not None  # false if this is part of an instrument
        # draw_property_on_split_row if main property to visually align with note property
        MidiPanel.draw_property(col, note_action_property, "id_type", i18n.get_label(i18n.TYPE),
                                is_main_property)
        if note_action_property.id_type is not None:
            object_row = col.row()
            object_row.enabled = not note_action_property.copy_to_selected_objects
            MidiPanel.draw_property(object_row, note_action_property,
                                    midi_data.ID_PROPERTIES_DICTIONARY[note_action_property.id_type][0],
                                    i18n.get_label(note_action_property.id_type), is_main_property)
            MidiPanel.draw_property(col, note_action_property, "action", i18n.get_label(i18n.ACTION), is_main_property)

        parent_layout.separator()

        col = parent_layout.column(align=True)
        if is_main_property:
            row = col.row()
            row.enabled = midi_data.can_resolve_data_from_selected_objects(note_action_property.id_type)
            row.prop(note_action_property, "copy_to_selected_objects")

        col.prop(note_action_property, "sync_length_with_notes")
        if note_action_property.sync_length_with_notes:
            PanelUtils.indented_row(col).prop(note_action_property, "sync_length_action_timing_mode")
            PanelUtils.indented_row(col).prop(note_action_property, "scale_factor")

        col.prop(note_action_property, "copy_to_note_end")

        col.prop(note_action_property, "add_filters")
        if note_action_property.add_filters:
            PanelUtils.draw_filter_box(col, note_action_property, not is_main_property, action_index, MidiDataType.NLA,
                                       context)

        col = parent_layout.column(align=True)
        col.prop(note_action_property, "on_overlap")
        if note_action_property.on_overlap == "DUPLICATE_OBJECT":
            action_length_row = PanelUtils.indented_row(col)
            action_length_row.prop(note_action_property, "action_length")
        elif note_action_property.on_overlap == "BLEND":
            blend_row = PanelUtils.indented_row(col)
            blend_row.prop(note_action_property, "blend_mode")
        col.prop(note_action_property, "nla_track_name")
        if is_main_property:
            col.prop(midi_data_property, "midi_frame_start")
        col.prop(note_action_property, "midi_frame_offset")

    @staticmethod
    def draw_property(parent_layout, data, prop, label, draw_on_split_row):
        if draw_on_split_row:
            PanelUtils.draw_property_on_split_row(parent_layout, data, label, prop)
        else:
            parent_layout.prop(data, prop)


class MidiInstrumentPanel(bpy.types.Panel):
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_category = i18n.get_key(i18n.MIDI_INSTRUMENTS)
    bl_label = i18n.get_key(i18n.NLA_MIDI_INSTRUMENTS)
    bl_idname = "ANIMATION_PT_midi_instrument_panel"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(context.scene.midi_data_property, "selected_instrument_id")

        selected_instrument = midi_data.get_midi_data(MidiDataType.NLA).selected_instrument(context)
        if selected_instrument is not None:
            self.draw_instrument_properties(selected_instrument)
            self.draw_instrument_notes(selected_instrument, context)
            self.draw_transpose_instrument(selected_instrument)
            self.draw_animate_instrument(context, selected_instrument)

        self.layout.separator()
        col = self.layout.column(align=True)
        col.operator(AddInstrument.bl_idname)
        col.operator(NLAMidiAllInstrumentCopier.bl_idname)

    def draw_animate_instrument(self, context, instrument):
        if context.scene.midi_data_property.midi_file:

            animate_box = \
                PanelUtils.draw_collapsible_box(self.layout, i18n.concat(i18n.get_text(i18n.ANIMATE), instrument.name),
                                                instrument, "animate_expanded")[0]
            if instrument.animate_expanded:
                animate_box.prop(instrument, "selected_midi_track")
                animate_box.prop(instrument, "copy_to_single_track")
                text_box_row = animate_box.row()
                text_box_row.prop(instrument, "nla_track_name")
                text_box_row.enabled = instrument.copy_to_single_track
                animate_box.operator(NLAMidiInstrumentCopier.bl_idname,
                                     text=i18n.concat(i18n.get_text(i18n.ANIMATE), instrument.name))

    def draw_instrument_notes(self, instrument, context):
        notes_box = \
            PanelUtils.draw_collapsible_box(self.layout, i18n.concat(instrument.name, i18n.get_text(i18n.NOTES)),
                                            instrument, "notes_expanded")[0]
        if instrument.notes_expanded:
            PanelUtils.draw_note_with_search(notes_box, instrument, "selected_note_id", "note_search_string")
            notes_box.operator(AddActionToInstrument.bl_idname)
            instrument_note_property = PropertyUtils.instrument_selected_note_property(instrument)
            if instrument_note_property is not None:
                for i in range(len(instrument_note_property.actions)):
                    self.draw_action(instrument_note_property.actions[i], i, notes_box, context)

    def draw_instrument_properties(self, instrument):
        box = \
            PanelUtils.draw_collapsible_box(self.layout, i18n.concat(instrument.name, i18n.get_text(i18n.PROPERTIES)),
                                            instrument, "properties_expanded")[0]

        if instrument.properties_expanded:
            box.prop(instrument, "name")
            box.prop(instrument, "instrument_midi_frame_offset")
            box.operator(DeleteInstrument.bl_idname, text=i18n.concat(i18n.get_text(i18n.DELETE), instrument.name))

    def draw_transpose_instrument(self, instrument):
        box = PanelUtils.draw_collapsible_box(self.layout, i18n.concat(i18n.get_text(i18n.TRANSPOSE), instrument.name),
                                              instrument, "transpose_expanded")[0]
        if instrument.transpose_expanded:
            box.prop(instrument, "transpose_filters")
            transpose_row = box.row()
            MidiInstrumentPanel.draw_transpose_operator(instrument, -12, i18n.get_key(i18n.MINUS_OCTAVE), transpose_row)
            MidiInstrumentPanel.draw_transpose_operator(instrument, -1, i18n.get_key(i18n.MINUS_STEP), transpose_row)
            MidiInstrumentPanel.draw_transpose_operator(instrument, +1, i18n.get_key(i18n.PLUS_STEP), transpose_row)
            MidiInstrumentPanel.draw_transpose_operator(instrument, +12, i18n.get_key(i18n.PLUS_OCTAVE), transpose_row)

    @staticmethod
    def draw_transpose_operator(instrument, steps: int, text: str, row: bpy.types.UILayout):
        col = row.column(align=True)
        transpose_operator = col.operator(TransposeInstrument.bl_idname, text=text)
        transpose_operator.transpose_steps = steps
        col.enabled = MidiInstrumentPanel.can_transpose(instrument, steps)

    @staticmethod
    def can_transpose(instrument, steps: int) -> bool:
        """
        :param instrument: the instrument
        :param steps: number of steps to transpose
        :return: true if the instrument can be transposed
        """
        can_transpose_notes = next(
            (x for x in instrument.notes if not PitchUtils.can_be_transposed(x.note_id, steps)), None) is None
        can_transpose_filters = True
        if instrument.transpose_filters == "transpose_all":
            can_transpose_filters = MidiInstrumentPanel.can_transpose_filters(
                instrument, lambda pitch, comparison_operator: PitchUtils.can_be_transposed(pitch, steps))
        elif instrument.transpose_filters == "transpose_all_leave_all_inclusive":
            can_transpose_filters = MidiInstrumentPanel.can_transpose_filters(
                instrument,
                lambda pitch, comparison_operator: PitchUtils.pitch_filter_is_all_inclusive(pitch, comparison_operator)
                                                   or PitchUtils.can_be_transposed(pitch, steps))
        return can_transpose_notes and can_transpose_filters

    @staticmethod
    def can_transpose_filters(instrument, can_transpose_lambda: Callable[[int, str], bool]) -> bool:
        """
        :param instrument: the instrument
        :param can_transpose_lambda: lambda that takes a pitch and comparison operator and returns a boolean
        :return: true if the instrument's filters can be transposed
        """
        for instrument_note in instrument.notes:
            for note_action in instrument_note.actions:
                if note_action.add_filters:
                    for filter_group in note_action.note_filter_groups:
                        for note_filter in filter_group.note_filters:
                            if note_filter.filter_type == "note_pitch_filter":
                                if not PitchUtils.note_id_is_selected_note(note_filter.note_pitch):
                                    pitch = PitchUtils.note_pitch_from_id(note_filter.note_pitch)
                                    if not can_transpose_lambda(pitch, note_filter.comparison_operator):
                                        return False
        return True

    def draw_action(self, action, action_index: int, parent: bpy.types.UILayout, context) -> None:
        collapsible_box = PanelUtils.draw_collapsible_box(parent, action.name, action, "expanded",
                                                          RemoveActionFromInstrument.bl_idname)
        box = collapsible_box[0]
        remove_operator = collapsible_box[1]
        remove_operator.action_index = action_index

        if action.expanded:
            box.prop(action, "name")
            MidiPanel.draw_note_action_common(box, box.column(align=True), action, context, action_index=action_index)


class QuickCopyPanel(bpy.types.Panel):
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_category = i18n.get_key(i18n.MIDI)
    bl_label = i18n.get_key(i18n.QUICK_COPY_TOOLS)
    bl_idname = "ANIMATION_PT_nla_midi_quick_copy_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        col = self.layout.column(align=True)
        midi_data_property = context.scene.midi_data_property
        bulk_copy_property = midi_data_property.bulk_copy_property
        quick_copy_tool = bulk_copy_property.quick_copy_tool

        col.prop(bulk_copy_property, "quick_copy_tool")
        col.separator()
        col = self.layout.column(align=True)

        if quick_copy_tool == "copy_to_instrument":
            PanelUtils.draw_note_with_search(col, midi_data_property, "copy_to_instrument_selected_note_id",
                                             "copy_to_instrument_note_search_string")
            self.draw_copy_to_instrument_option(col, bulk_copy_property, midi_data_property, True)
        elif quick_copy_tool == "copy_along_path":
            col.prop(bulk_copy_property, "bulk_copy_curve")
            PanelUtils.draw_note_with_search(col, bulk_copy_property, "bulk_copy_starting_note",
                                             "bulk_copy_starting_note_search_string")
            PanelUtils.draw_scale_filter(col, bulk_copy_property, "scale_filter_type", "scale_filter_scale")
            col.prop(bulk_copy_property, "only_notes_in_selected_track")

            self.draw_copy_to_instrument_option(col, bulk_copy_property, midi_data_property)
        elif quick_copy_tool == "copy_by_object_name":
            col.prop(bulk_copy_property, "copy_by_name_type")
            col.prop(bulk_copy_property, "selected_objects_only")
            self.draw_copy_to_instrument_option(col, bulk_copy_property, midi_data_property)

        copy_to_instrument = quick_copy_tool == "copy_to_instrument" or bulk_copy_property.copy_to_instrument
        if quick_copy_tool == "copy_to_instrument":
            base_tooltip = i18n.get_text(i18n.COPY_ACTION_TO_INSTRUMENT)
        else:
            base_tooltip = i18n.get_text(i18n.COPY_ACTIONS_TO_INSTRUMENT) if copy_to_instrument else \
                i18n.get_text(i18n.COPY_ACTIONS_TO_SELECTED_OBJECTS)
        animate_button_text = i18n.get_key(i18n.COPY_TO_INSTRUMENT_OP) if \
            (bulk_copy_property.copy_to_instrument or quick_copy_tool == "copy_to_instrument") \
            else i18n.get_key(i18n.COPY_ACTION_TO_NOTES_OP)
        tooltip_creator = self.copy_button_tooltip_creator(midi_data_property, bulk_copy_property, copy_to_instrument,
                                                           base_tooltip, animate_button_text)
        tooltip_creator.draw_operator_row(col)

    @staticmethod
    def draw_copy_to_instrument_option(parent_layout, bulk_copy_property, midi_data_property,
                                       instrument_only: bool = False):
        if instrument_only:
            instrument_row = parent_layout.row()
        else:
            parent_layout.prop(bulk_copy_property, "copy_to_instrument")
            instrument_row = PanelUtils.indented_row(parent_layout)
            instrument_row.enabled = bulk_copy_property.copy_to_instrument
        instrument_row.prop(midi_data_property, "copy_to_instrument_selected_instrument")

    @staticmethod
    def copy_button_tooltip_creator(midi_data_property, bulk_copy_property, copy_to_instrument: bool,
                                    base_tooltip: str, button_text: str) -> PanelUtils.OperatorTooltipCreator:
        tooltip_creator = PanelUtils.OperatorTooltipCreator(NLABulkMidiCopier, base_tooltip=base_tooltip,
                                                            button_text=button_text)

        note_action_property = midi_data_property.note_action_property

        quick_copy_tool = bulk_copy_property.quick_copy_tool
        if quick_copy_tool == "copy_along_path":
            if bulk_copy_property.bulk_copy_curve is None:
                tooltip_creator.add_disable_description(i18n.get_text_tip(i18n.NO_PATH_SELECTED))

            # copy along path only works if the id_type corresponds to an object type
            if not midi_data.can_resolve_data_from_selected_objects(note_action_property.id_type):
                tooltip_creator.add_disable_description(
                    i18n.concat(i18n.get_text_tip(i18n.COPY_ALONG_PATH_DOES_NOT_WITH_WORK_TYPE),
                                note_action_property.id_type))
        elif quick_copy_tool == "copy_by_object_name":
            # copy by object name only works if the id_type corresponds to an object type
            if not midi_data.can_resolve_data_from_selected_objects(note_action_property.id_type):
                tooltip_creator.add_disable_description(
                    i18n.concat(i18n.get_text_tip(i18n.COPY_BY_OBJECT_NAME_DOES_NOT_WITH_WORK_TYPE),
                                note_action_property.id_type))
        elif quick_copy_tool == "copy_to_instrument":
            if note_action_property.copy_to_selected_objects:
                tooltip_creator.add_disable_description(
                    i18n.get_text_tip(i18n.COPY_TO_SELECTED_OBJECTS_NOT_VALID_FOR_INSTRUMENTS))

        if copy_to_instrument:
            if midi_data_property.copy_to_instrument_selected_instrument is None or \
                    midi_data_property.copy_to_instrument_selected_instrument == PropertyUtils.NO_SELECTION:
                tooltip_creator.add_disable_description(i18n.get_text_tip(i18n.NO_INSTRUMENT_SELECTED))
        else:
            midi_file = midi_data_property.midi_file
            if midi_file is None or len(midi_file) == 0:
                tooltip_creator.add_disable_description(i18n.get_text_tip(i18n.NO_MIDI_FILE_SELECTED))
            if note_action_property.action is None:
                tooltip_creator.add_disable_description(i18n.get_text_tip(i18n.NO_ACTION_SELECTED_IN_MLA_MIDI_PANEL))

        return tooltip_creator


class MidiSettingsPanel(bpy.types.Panel):
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_category = i18n.get_key(i18n.MIDI)
    bl_label = i18n.get_key(i18n.MIDI_SETTINGS)
    bl_idname = "ANIMATION_PT_midi_settings_panel"

    def draw(self, context):
        PanelUtils.draw_common_midi_settings(self.layout, context, MidiDataType.NLA)


class OtherToolsPanel(bpy.types.Panel):
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_category = i18n.get_key(i18n.MIDI)
    bl_label = i18n.get_key(i18n.OTHER_TOOLS)
    bl_idname = "ANIMATION_PT_midi_other_tools_panel"

    def draw(self, context):
        midi_data_property = context.scene.midi_data_property
        col = self.layout.column(align=True)
        col.prop(midi_data_property.other_tool_property, "selected_tool")
        col.separator()
        if midi_data_property.other_tool_property.selected_tool == "rename_action":
            self.draw_rename_action(context, col, midi_data_property)
        elif midi_data_property.other_tool_property.selected_tool == "generate_transitions":
            self.draw_generate_transitions(context, col, midi_data_property)
        elif midi_data_property.other_tool_property.selected_tool == "delete_transitions":
            self.draw_delete_transitions(context, col)

    def draw_rename_action(self, context, layout, midi_data_property):
        other_tool_property = midi_data_property.other_tool_property
        rename_action_source = other_tool_property.rename_action_source
        layout.prop(other_tool_property, "rename_action_source")
        if rename_action_source == "selected":
            layout.prop(other_tool_property, "selected_rename_action")

        action = None
        if rename_action_source == "selected_nla_strip":
            if context.active_nla_strip is not None:
                action = context.active_nla_strip.action
        elif rename_action_source == "nla_midi_panel":
            action = midi_data_property.note_action_property.action
        elif rename_action_source == "selected":
            action = other_tool_property.selected_rename_action
        if action is not None:
            layout.prop(action, "name", text=i18n.get_key(i18n.ACTION_NAME))

    def draw_active_nla_track(self, context, layout):
        left, right, active_track_row = PanelUtils.split_row(layout, .2)
        right.enabled = False
        active_nla_track = context.active_nla_track
        left.label(text=i18n.get_label(i18n.get_key(i18n.ACTIVE_NLA_TRACK)))
        if active_nla_track is not None:
            # label instead of text argument so that label is not greyed out
            right.prop(active_nla_track, "name", text="")
        else:
            right.label(text=i18n.get_key(i18n.get_key(i18n.NO_NLA_TRACK_SELECTED)))


    def draw_generate_transitions(self, context, col, midi_data_property):
        # active_nla_track not added until blender 2.80. not going to iterate over every single animation data here
        # self.draw_active_nla_track(context, col)
        other_tool_property = midi_data_property.other_tool_property
        keframe_properties = other_tool_property.keyframe_properties
        col.prop(keframe_properties, "interpolation")
        if ActionUtils.interpolation_has_easing(keframe_properties.interpolation):
            col.prop(keframe_properties, "easing")
        col.prop(other_tool_property, "limit_transition_length")
        if other_tool_property.limit_transition_length:
            PanelUtils.indented_row(col).prop(other_tool_property, "transition_limit_frames")
            PanelUtils.indented_row(col).prop(other_tool_property, "transition_offset_frames")
            PanelUtils.indented_row(col).prop(other_tool_property, "transition_placement")
        col.prop(other_tool_property, "replace_transition_strips")

        col.separator()
        tooltip_creator = PanelUtils.OperatorTooltipCreator(GenerateTransitionsOperator)
        # active_nla_track not added until blender 2.80. not going to iterate over every single animation data here
        # if context.active_nla_track is None:
        #     tooltip_creator.add_disable_description(i18n.get_key(i18n.NO_NLA_TRACK_SELECTED))
        tooltip_creator.draw_operator_row(col)

    def draw_delete_transitions(self, context, col):
        # active_nla_track not added until blender 2.80. not going to iterate over every single animation data here
        # self.draw_active_nla_track(context, col)
        tooltip_creator = PanelUtils.OperatorTooltipCreator(DeleteTransitionsOperator)
        # active_nla_track not added until blender 2.80. not going to iterate over every single animation data here
        # if context.active_nla_track is None:
        #     tooltip_creator.add_disable_description(i18n.get_key(i18n.NO_NLA_TRACK_SELECTED))
        tooltip_creator.draw_operator_row(col)


# noinspection PyPep8Naming
class MIDI_TRACK_PROPERTIES_UL_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            text = item.midi_track_name
            if len(item.displayed_track_name.strip()) > 0:
                text = text + " (" + item.displayed_track_name + ")"
            layout.label(text=text, translate=False, icon='GREASEPENCIL')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='OUTLINER_DATA_GP_LAYER')
