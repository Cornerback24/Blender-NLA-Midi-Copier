if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NLAMidiCopierModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiInstrumentModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PropertyUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PanelUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PitchUtils)
else:
    # noinspection PyUnresolvedReferences
    from . import midi_data
    # noinspection PyUnresolvedReferences
    from . import NLAMidiCopierModule
    # noinspection PyUnresolvedReferences
    from . import MidiInstrumentModule
    # noinspection PyUnresolvedReferences
    from . import NoteFilterModule
    # noinspection PyUnresolvedReferences
    from . import PropertyUtils
    # noinspection PyUnresolvedReferences
    from . import PanelUtils
    # noinspection PyUnresolvedReferences
    from . import NoteFilterImplementations
    # noinspection PyUnresolvedReferences
    from . import PitchUtils

import bpy
from typing import Callable
from .NLAMidiCopierModule import NLAMidiCopier, NLAMidiInstrumentCopier, NLAMidiAllInstrumentCopier
from .MidiInstrumentModule import AddInstrument, DeleteInstrument, AddActionToInstrument, RemoveActionFromInstrument, \
    TransposeInstrument, CopyMidiPanelActionToInstrument
from . import midi_data
from bpy.props import EnumProperty


class MidiFileSelector(bpy.types.Operator):
    bl_idname = "ops.midi_file_selector"
    bl_label = "Select Midi File"
    # noinspection PyArgumentList,PyUnresolvedReferences
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.midi_data_property["midi_file"] = self.filepath
        try:
            midi_data.midi_data.update_midi_file(self.filepath, True, context)
        except Exception as e:
            self.report({"WARNING"}, "Could not load midi file: " + str(e))
            context.scene.midi_data_property["midi_file"] = ""
            midi_data.midi_data.update_midi_file(None, False, context)

        return {'FINISHED'}

    # noinspection PyUnusedLocal
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MidiPanel(bpy.types.Panel):
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_category = "Midi"
    bl_label = "NLA Midi"
    bl_idname = "ANIMATION_PT_midi_panel"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator(MidiFileSelector.bl_idname, text="Choose midi file", icon='FILE_FOLDER')

        midi_data_property = context.scene.midi_data_property
        midi_file = midi_data_property.midi_file
        if midi_data_property.midi_file:
            try:
                midi_data.midi_data.update_midi_file(midi_data_property.midi_file, False, context)
                col.prop(midi_data_property, "midi_file")

                col.prop(midi_data_property, "track_list")
                col.prop(midi_data_property, "notes_list")
            except Exception as e:
                print("Could not load midi file: " + str(e))
                midi_data.midi_data.update_midi_file(None, False, context)

        note_action_property = midi_data_property.note_action_property

        MidiPanel.draw_note_action_common(self.layout, col, note_action_property, midi_data_property=midi_data_property)

        self.layout.separator()

        col = self.layout.column(align=True)
        copy_to_notes_button_row = col.row()
        enable_copy_to_notes_button = midi_file is not None and len(midi_file) > 0 and \
                                      note_action_property.action is not None
        copy_to_notes_button_row.enabled = enable_copy_to_notes_button
        copy_to_notes_button_row.operator(NLAMidiCopier.bl_idname, icon='FILE_SOUND')

    @staticmethod
    def draw_note_action_common(parent_layout, col, note_action_property, midi_data_property=None, action_index=None):
        is_main_property = midi_data_property is not None  # false if this is part of a instrument
        col.prop(note_action_property, "id_type")
        if note_action_property.id_type is not None:
            col.prop(note_action_property, midi_data.ID_PROPERTIES_DICTIONARY[note_action_property.id_type][0])
            col.prop(note_action_property, "action")

        parent_layout.separator()

        col = parent_layout.column(align=True)
        col.enabled = note_action_property.id_type == "Object"
        if is_main_property:
            col.prop(note_action_property, "copy_to_selected_objects")
        col.prop(note_action_property, "duplicate_object_on_overlap")
        if note_action_property.action and note_action_property.duplicate_object_on_overlap:
            row = col.row()
            row.prop(note_action_property, "action_length")
        col = parent_layout.column(align=True)
        col.prop(note_action_property, "sync_length_with_notes")
        if note_action_property.sync_length_with_notes:
            col.prop(note_action_property, "scale_factor")
        col.prop(note_action_property, "add_filters")
        if note_action_property.add_filters:
            PanelUtils.draw_filter_box(col, note_action_property, not is_main_property, action_index, "midi_data")

        col = parent_layout.column(align=True)
        col.prop(note_action_property, "blend_mode")
        col.prop(note_action_property, "nla_track_name")
        if is_main_property:
            col.prop(midi_data_property, "midi_frame_start")
        col.prop(note_action_property, "midi_frame_offset")


class MidiInstrumentPanel(bpy.types.Panel):
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_category = "Midi Instruments"
    bl_label = "NLA Midi Instruments"
    bl_idname = "ANIMATION_PT_midi_instrument_panel"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(context.scene.midi_data_property, "selected_instrument_id")

        selected_instrument = midi_data.midi_data.selected_instrument(context)
        if selected_instrument is not None:
            self.draw_instrument_properties(selected_instrument)
            self.draw_instrument_notes(selected_instrument)
            self.draw_transpose_instrument(selected_instrument)
            self.draw_animate_instrument(context, selected_instrument)

        self.layout.separator()
        col = self.layout.column(align=True)
        col.operator(AddInstrument.bl_idname)
        col.operator(NLAMidiAllInstrumentCopier.bl_idname)

    def draw_animate_instrument(self, context, instrument):
        if context.scene.midi_data_property.midi_file:
            try:
                midi_data.midi_data.update_midi_file(context.scene.midi_data_property.midi_file, False, context)
                animate_box = PanelUtils.draw_collapsible_box(self.layout, "Animate " + instrument.name, instrument,
                                                              "animate_expanded")[0]
                if instrument.animate_expanded:
                    animate_box.prop(instrument, "selected_midi_track")
                    animate_box.prop(instrument, "copy_to_single_track")
                    text_box_row = animate_box.row()
                    text_box_row.prop(instrument, "nla_track_name")
                    text_box_row.enabled = instrument.copy_to_single_track
                    animate_box.operator(NLAMidiInstrumentCopier.bl_idname, text="Animate " + instrument.name)
            except Exception as e:
                print("Could not load midi file: " + str(e))
                midi_data.midi_data.update_midi_file(None, False, context)

    def draw_instrument_notes(self, instrument):
        notes_box = PanelUtils.draw_collapsible_box(self.layout, instrument.name + " Notes", instrument,
                                                    "notes_expanded")[0]
        if instrument.notes_expanded:
            notes_box.prop(instrument, "selected_note_id")
            notes_box.prop(instrument, "note_search_string")
            notes_box.operator(AddActionToInstrument.bl_idname)
            instrument_note_property = PropertyUtils.instrument_selected_note_property(instrument)
            if instrument_note_property is not None:
                for i in range(len(instrument_note_property.actions)):
                    self.draw_action(instrument_note_property.actions[i], i, notes_box)

    def draw_instrument_properties(self, instrument):
        box = PanelUtils.draw_collapsible_box(self.layout, instrument.name + " Properties", instrument,
                                              "properties_expanded")[0]

        if instrument.properties_expanded:
            box.prop(instrument, "name")
            box.prop(instrument, "instrument_midi_frame_offset")
            box.operator(DeleteInstrument.bl_idname, text="Delete " + instrument.name)

    def draw_transpose_instrument(self, instrument):
        box = PanelUtils.draw_collapsible_box(self.layout, "Transpose " + instrument.name, instrument,
                                              "transpose_expanded")[0]
        if instrument.transpose_expanded:
            box.prop(instrument, "transpose_filters")
            transpose_row = box.row()
            MidiInstrumentPanel.draw_transpose_operator(instrument, -12, "- octave", transpose_row)
            MidiInstrumentPanel.draw_transpose_operator(instrument, -1, "- step", transpose_row)
            MidiInstrumentPanel.draw_transpose_operator(instrument, +1, "+ step", transpose_row)
            MidiInstrumentPanel.draw_transpose_operator(instrument, +12, "+ octave", transpose_row)

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
                                pitch = PitchUtils.note_pitch_from_id(note_filter.note_pitch)
                                if not can_transpose_lambda(pitch, note_filter.comparison_operator):
                                    return False
        return True

    def draw_action(self, action, action_index: int, parent: bpy.types.UILayout) -> None:
        collapsible_box = PanelUtils.draw_collapsible_box(parent, action.name, action, "expanded",
                                                          RemoveActionFromInstrument.bl_idname)
        box = collapsible_box[0]
        remove_operator = collapsible_box[1]
        remove_operator.action_index = action_index

        if action.expanded:
            box.prop(action, "name")
            MidiPanel.draw_note_action_common(box, box.column(align=True), action, action_index=action_index)


class CopyToInstrumentPanel(bpy.types.Panel):
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_category = "Midi"
    bl_label = "Copy to Instrument"
    bl_idname = "ANIMATION_PT_midi_copy_to_instrument_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        col = self.layout.column(align=True)
        midi_data_property = context.scene.midi_data_property
        col.prop(midi_data_property, "copy_to_instrument_selected_instrument")
        col.prop(midi_data_property, "copy_to_instrument_selected_note_id")
        col.prop(midi_data_property, "copy_to_instrument_note_search_string")
        copy_button_row = col.row()
        copy_button_row.enabled = midi_data_property.copy_to_instrument_selected_instrument is not None and \
                                  midi_data_property.copy_to_instrument_selected_instrument \
                                  != midi_data.NO_INSTRUMENT_SELECTED and \
                                  not midi_data_property.note_action_property.copy_to_selected_objects
        copy_button_row.operator(CopyMidiPanelActionToInstrument.bl_idname)


class MidiSettingsPanel(bpy.types.Panel):
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_category = "Midi"
    bl_label = "Midi Settings"
    bl_idname = "ANIMATION_PT_midi_settings_panel"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(context.scene.midi_data_property, "middle_c_note")
