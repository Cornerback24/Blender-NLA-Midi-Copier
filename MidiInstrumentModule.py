if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PropertyUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PitchUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(CollectionUtils)
else:
    from . import midi_data
    from . import PropertyUtils
    from . import PitchUtils
    from . import CollectionUtils
    from .i18n import i18n

import bpy
from .midi_data import MidiDataType


class NLA_MIDI_COPIER_OT_add_instrument(bpy.types.Operator):
    bl_idname = "nla_midi_copier.add_instrument"
    bl_label = i18n.get_key(i18n.CREATE_NEW_INSTRUMENT_OP)
    bl_description = i18n.get_key(i18n.CREATE_NEW_INSTRUMENT_DESCRIPTION)
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        CollectionUtils.add_to_collection(context.scene.midi_data_property.instruments, i18n.get_text(i18n.INSTRUMENT),
                                          context.scene.midi_data_property, "selected_instrument_id")


class NLA_MIDI_COPIER_OT_delete_instrument(bpy.types.Operator):
    bl_idname = "nla_midi_copier.delete_instrument"
    bl_label = i18n.get_key(i18n.DELETE_INSTRUMENT_OP)
    bl_description = i18n.get_key(i18n.DELETE_INSTRUMENT_DESCRIPTION)
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return midi_data.get_midi_data(MidiDataType.NLA).selected_instrument(context) is not None

    def action_common(self, context):
        CollectionUtils.remove_from_collection(
            context.scene.midi_data_property.instruments, midi_data.get_midi_data_property(MidiDataType.NLA, context),
            "selected_instrument_id")


class NLA_MIDI_COPIER_OT_add_action_to_instrument(bpy.types.Operator):
    bl_idname = "nla_midi_copier.add_action_to_instrument"
    bl_label = i18n.get_key(i18n.ADD_ACTION_OP)
    bl_description = i18n.get_key(i18n.ADD_ACTION_TO_INSTRUMENT_DESCRIPTION)
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        instrument = midi_data.get_midi_data(MidiDataType.NLA).selected_instrument(context)
        if instrument is not None:
            # create new action for instrument
            PropertyUtils.get_note_action_property(instrument, int(instrument.selected_note_id))


class NLA_MIDI_COPIER_OT_remove_action_from_instrument(bpy.types.Operator):
    bl_idname = "nla_midi_copier.remove_action_from_instrument"
    bl_label = i18n.get_key(i18n.DELETE_ACTION_OP)
    bl_description = i18n.get_key(i18n.DELETE_ACTION)
    bl_options = {"REGISTER", "UNDO"}

    action_index: bpy.props.IntProperty(name="Index", options={'HIDDEN'})

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        instrument = midi_data.get_midi_data(MidiDataType.NLA).selected_instrument(context)
        if instrument is not None:

            instrument_note_property = PropertyUtils.instrument_selected_note_property(instrument)
            instrument_note_property.actions.remove(self.properties.action_index)

            # don't store an empty list of actions if there are no more actions for the note
            if len(instrument_note_property.actions) == 0:
                index = None
                for i in range(len(instrument.notes)):
                    if instrument.notes[i] == instrument_note_property:
                        index = i
                if index is not None:
                    instrument.notes.remove(index)


class NLA_MIDI_COPIER_OT_transpose_instrument(bpy.types.Operator):
    bl_idname = "nla_midi_copier.transpose_instrument"
    bl_label = i18n.get_key(i18n.TRANSPOSE_INSTRUMENT_OP)
    bl_description = i18n.get_key(i18n.TRANSPOSE_INSTRUMENT)
    bl_options = {"REGISTER", "UNDO"}

    transpose_steps: bpy.props.IntProperty(name=i18n.get_key(i18n.TRANSPOSE_STEPS))

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        instrument = midi_data.get_midi_data(MidiDataType.NLA).selected_instrument(context)
        for note in instrument.notes:
            note.note_id += self.properties.transpose_steps
        if instrument.transpose_filters == "transpose_all":
            self.transpose_filters(instrument, lambda pitch, comparison_operator: True)
        elif instrument.transpose_filters == "transpose_all_leave_all_inclusive":
            self.transpose_filters(
                instrument,
                lambda pitch, comparison_operator:
                not PitchUtils.pitch_filter_is_all_inclusive(pitch, comparison_operator))
        elif instrument.transpose_filters == "transpose_if_possible":
            self.transpose_filters(
                instrument,
                lambda pitch, comparison_operator:
                PitchUtils.can_be_transposed(pitch, self.properties.transpose_steps))
        elif instrument.transpose_filters == "transpose_if_possible_leave_all_inclusive":
            self.transpose_filters(
                instrument,
                lambda pitch, comparison_operator:
                not (PitchUtils.pitch_filter_is_all_inclusive(pitch, comparison_operator)) and
                PitchUtils.can_be_transposed(pitch, self.properties.transpose_steps))
        # Change the selected note to the pitch the previous selected note was transposed to. If the change would be to
        # a pitch less than 0 or greater than 127, set to 0 or 127
        instrument.selected_note_id = str(
            min(127, max(0, int(instrument.selected_note_id) + self.properties.transpose_steps)))

    def transpose_filters(self, instrument, should_transpose):
        """
        :param instrument: the instrument
        :param should_transpose: lambda that takes a pitch and comparison operator and returns a boolean
        :return: true if the instrument's filters can be transposed
        """
        transpose_steps = self.properties.transpose_steps
        for instrument_note in instrument.notes:
            for note_action in instrument_note.actions:
                if note_action.add_filters:
                    for filter_group in note_action.note_filter_groups:
                        for note_filter in filter_group.note_filters:
                            if note_filter.filter_type == "note_pitch_filter":
                                if not PitchUtils.note_id_is_selected_note(note_filter.note_pitch):
                                    pitch = PitchUtils.note_pitch_from_id(note_filter.note_pitch)
                                    if should_transpose(pitch, note_filter.comparison_operator):
                                        note_filter.note_pitch = PitchUtils.note_id_from_pitch(pitch + transpose_steps)
