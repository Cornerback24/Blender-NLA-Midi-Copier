if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PropertyUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PitchUtils)
else:
    from . import midi_data
    from . import PropertyUtils
    from . import PitchUtils
import bpy


class AddInstrument(bpy.types.Operator):
    bl_idname = "ops.nla_midi_add_instrument"
    bl_label = "Create New Instrument"
    bl_description = "Create a new instrument.  An instrument defines one or many actions for each note"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        instruments = context.scene.midi_data_property.instruments
        new_instrument = instruments.add()
        new_instrument.name = "Instrument " + str(len(instruments))
        context.scene.midi_data_property.selected_instrument_id = str(len(instruments) - 1)


class DeleteInstrument(bpy.types.Operator):
    bl_idname = "ops.nla_midi_delete_instrument"
    bl_label = "Delete Instrument"
    bl_description = "Delete the selected instrument"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return midi_data.midi_data.selected_instrument_id(context) is not None

    def action_common(self, context):
        instruments = context.scene.midi_data_property.instruments
        selected_instrument_id = midi_data.midi_data.selected_instrument_id(context)
        if selected_instrument_id is not None:
            instrument_index = int(selected_instrument_id)
            context.scene.midi_data_property.selected_instrument_id = midi_data.NO_INSTRUMENT_SELECTED
            instruments.remove(instrument_index)


class AddActionToInstrument(bpy.types.Operator):
    bl_idname = "ops.nla_midi_add_action_to_instrument"
    bl_label = "Add Action"
    bl_description = "Add an action for the selected note"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        instrument = midi_data.selected_instrument(context)
        if instrument is not None:
            # create new action for instrument
            AddActionToInstrument.get_note_action_property(instrument, int(instrument.selected_note_id))

    @staticmethod
    def get_note_action_property(instrument, note_id: int):
        instrument_note_property = next((x for x in instrument.notes if x.note_id == note_id), None)
        if instrument_note_property is None:
            instrument_note_property = instrument.notes.add()
            instrument_note_property.note_id = note_id

        note_action_property = instrument_note_property.actions.add()
        note_action_property.name = "Action " + str(len(instrument_note_property.actions))
        return note_action_property


class CopyMidiPanelActionToInstrument(bpy.types.Operator):
    bl_idname = "ops.nla_midi_copy_midi_panel_action_to_instrument"
    bl_label = "Copy to Instrument"
    bl_description = "Copy the action to the selected instrument"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        instrument = midi_data.midi_data.selected_instrument_for_copy_to_id(context)
        if instrument is None:
            return
        note_id: str = context.scene.midi_data_property.copy_to_instrument_selected_note_id
        copied_note_action_property = AddActionToInstrument.get_note_action_property(instrument, int(note_id))
        midi_panel_note_action_property = context.scene.midi_data_property.note_action_property
        CopyMidiPanelActionToInstrument.copy_note_action_property(midi_panel_note_action_property,
                                                                  copied_note_action_property)

    @staticmethod
    def copy_note_action_property(copy_from, copy_to):
        copy_to.id_type = copy_from.id_type
        copy_to.action = copy_from.action
        copy_to.midi_frame_offset = copy_from.midi_frame_offset
        copy_to.nla_track_name = copy_from.nla_track_name
        copy_to.duplicate_object_on_overlap = copy_from.duplicate_object_on_overlap
        copy_to.blend_mode = copy_from.blend_mode
        copy_to.sync_length_with_notes = copy_from.sync_length_with_notes
        copy_to.add_filters = copy_from.add_filters
        copy_to.filters_expanded = copy_from.filters_expanded
        copy_to.action_length = copy_from.action_length
        copy_to.scale_factor = copy_from.scale_factor

        for copy_from_filter_group in copy_from.note_filter_groups:
            copy_to_filter_group = copy_to.note_filter_groups.add()
            for copy_from_filter in copy_from_filter_group.note_filters:
                copy_to_filter = copy_to_filter_group.note_filters.add()
                copy_to_filter.filter_type = copy_from_filter.filter_type
                copy_to_filter.comparison_operator = copy_from_filter.comparison_operator
                copy_to_filter.note_pitch = copy_from_filter.note_pitch
                copy_to_filter.non_negative_int = copy_from_filter.non_negative_int
                copy_to_filter.positive_int = copy_from_filter.positive_int
                copy_to_filter.positive_int_2 = copy_from_filter.positive_int_2
                copy_to_filter.int_0_to_127 = copy_from_filter.int_0_to_127
                copy_to_filter.non_negative_number = copy_from_filter.non_negative_number
                copy_to_filter.time_unit = copy_from_filter.time_unit

        animated_object_property = midi_data.ID_PROPERTIES_DICTIONARY[copy_from.id_type][0]
        setattr(copy_to, animated_object_property, getattr(copy_from, animated_object_property))


class RemoveActionFromInstrument(bpy.types.Operator):
    bl_idname = "ops.nla_midi_remove_action_from_instrument"
    bl_label = "Delete Action"
    bl_description = "Delete action"
    bl_options = {"REGISTER", "UNDO"}

    action_index: bpy.props.IntProperty(name="Index")

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        instrument = midi_data.selected_instrument(context)
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


class TransposeInstrument(bpy.types.Operator):
    bl_idname = "ops.nla_midi_transpose_instrument"
    bl_label = "Transpose Instrument"
    bl_description = "Transpose Instrument"
    bl_options = {"REGISTER", "UNDO"}

    transpose_steps: bpy.props.IntProperty(name="Transpose Steps")

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        instrument = midi_data.selected_instrument(context)
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
        # change the selected note to the pitch the previous selected note was transposed to
        instrument.selected_note_id = str(int(instrument.selected_note_id) + self.properties.transpose_steps)

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
                                pitch = PitchUtils.note_pitch_from_id(note_filter.note_pitch)
                                if should_transpose(pitch, note_filter.comparison_operator):
                                    note_filter.note_pitch = PitchUtils.note_id_from_pitch(pitch + transpose_steps)
