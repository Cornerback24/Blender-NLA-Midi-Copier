if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PropertyUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(CollectionUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from . import midi_data
    from . import PropertyUtils
    from . import CollectionUtils
    from .i18n import i18n

import bpy


class NLA_MIDI_COPIER_OT_add_note_filter(bpy.types.Operator):
    bl_idname = "nla_midi_copier.add_note_filter"
    bl_label = i18n.get_key(i18n.ADD_FILTER_OP)
    bl_description = i18n.get_key(i18n.ADD_A_FILTER)
    bl_options = {"REGISTER", "UNDO"}

    is_part_of_instrument: bpy.props.BoolProperty(name="IsPartOfInstrument", options={'HIDDEN'})
    action_index: bpy.props.IntProperty(name="ActionIndex", options={'HIDDEN'})
    filter_group_index: bpy.props.IntProperty(name="FilterGroupIndex", options={'HIDDEN'})
    midi_data_type: bpy.props.IntProperty(name="MidiDataType", options={'HIDDEN'})

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        note_action_property = PropertyUtils.selected_note_property(midi_data.get_midi_data(self.midi_data_type),
                                                                    self.properties.is_part_of_instrument,
                                                                    self.properties.action_index,
                                                                    context)
        filter_group_property = note_action_property.note_filter_groups[self.filter_group_index]
        filter_group_property.note_filters.add()


class NLA_MIDI_COPIER_OT_remove_note_filter(bpy.types.Operator):
    bl_idname = "nla_midi_copier.remove_note_filter"
    bl_label = i18n.get_key(i18n.REMOVE_FILTER_OP)
    bl_description = i18n.get_key(i18n.REMOVE_FILTER)
    bl_options = {"REGISTER", "UNDO"}

    is_part_of_instrument: bpy.props.BoolProperty(name="IsPartOfInstrument", options={'HIDDEN'})
    action_index: bpy.props.IntProperty(name="ActionIndex", options={'HIDDEN'})
    filter_group_index: bpy.props.IntProperty(name="FilterGroupIndex", options={'HIDDEN'})
    filter_index: bpy.props.IntProperty(name="FilterIndex", options={'HIDDEN'})
    midi_data_type: bpy.props.IntProperty(name="MidiDataType", options={'HIDDEN'})

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        note_action_property = PropertyUtils.selected_note_property(midi_data.get_midi_data(self.midi_data_type),
                                                                    self.properties.is_part_of_instrument,
                                                                    self.properties.action_index,
                                                                    context)
        filter_group_property = note_action_property.note_filter_groups[self.filter_group_index]
        filter_group_property.note_filters.remove(self.filter_index)


class NLA_MIDI_COPIER_OT_reorder_note_filter(bpy.types.Operator):
    bl_idname = "nla_midi_copier.reorder_note_filter"
    bl_label = i18n.get_key(i18n.REORDER_FILTER_OP)
    bl_description = i18n.get_key(i18n.CHANGE_FILTER_ORDER)
    bl_options = {"REGISTER", "UNDO"}

    is_part_of_instrument: bpy.props.BoolProperty(name="IsPartOfInstrument", options={'HIDDEN'})
    action_index: bpy.props.IntProperty(name="ActionIndex", options={'HIDDEN'})
    filter_group_index: bpy.props.IntProperty(name="FilterGroupIndex", options={'HIDDEN'})
    filter_index: bpy.props.IntProperty(name="FilterIndex", options={'HIDDEN'})
    reorder_factor: bpy.props.IntProperty(name="ReorderFactor", options={'HIDDEN'})
    midi_data_type: bpy.props.IntProperty(name="MidiDataType", options={'HIDDEN'})

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        note_action_property = PropertyUtils.selected_note_property(midi_data.get_midi_data(self.midi_data_type),
                                                                    self.properties.is_part_of_instrument,
                                                                    self.properties.action_index,
                                                                    context)
        filter_group_property = note_action_property.note_filter_groups[self.filter_group_index]
        filter_group_property.note_filters.move(self.filter_index, self.filter_index + self.reorder_factor)


class NLA_MIDI_COPIER_OT_add_note_filter_group(bpy.types.Operator):
    bl_idname = "nla_midi_copier.add_note_filter_group"
    bl_label = i18n.get_key(i18n.ADD_FILTER_GROUP_OP)
    bl_description = i18n.get_key(i18n.ADD_FILTER_GROUP_DESCRIPTION)
    bl_options = {"REGISTER", "UNDO"}

    is_part_of_instrument: bpy.props.BoolProperty(name="IsPartOfInstrument", options={'HIDDEN'})
    action_index: bpy.props.IntProperty(name="Index", options={'HIDDEN'})
    midi_data_type: bpy.props.IntProperty(name="MidiDataType", options={'HIDDEN'})

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        note_action_property = PropertyUtils.selected_note_property(midi_data.get_midi_data(self.midi_data_type),
                                                                    self.properties.is_part_of_instrument,
                                                                    self.properties.action_index,
                                                                    context)
        filter_groups = note_action_property.note_filter_groups
        filter_groups.add()


class NLA_MIDI_COPIER_OT_remove_note_filter_group(bpy.types.Operator):
    bl_idname = "nla_midi_copier.remove_note_filter_group"
    bl_label = i18n.get_key(i18n.REMOVE_FILTER_GROUP_OP)
    bl_description = i18n.get_key(i18n.DELETE_FILTER_GROUP)
    bl_options = {"REGISTER", "UNDO"}

    is_part_of_instrument: bpy.props.BoolProperty(name="IsPartOfInstrument", options={'HIDDEN'})
    action_index: bpy.props.IntProperty(name="ActionIndex", options={'HIDDEN'})
    filter_group_index: bpy.props.IntProperty(name="FilterGroupIndex", options={'HIDDEN'})
    midi_data_type: bpy.props.IntProperty(name="MidiDataType", options={'HIDDEN'})

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        note_action_property = PropertyUtils.selected_note_property(midi_data.get_midi_data(self.midi_data_type),
                                                                    self.properties.is_part_of_instrument,
                                                                    self.properties.action_index,
                                                                    context)
        note_action_property.note_filter_groups.remove(self.filter_group_index)


class NLA_MIDI_COPIER_OT_add_note_filter_preset(bpy.types.Operator):
    bl_idname = "nla_midi_copier.add_note_filter_preset"
    bl_label = i18n.get_key(i18n.NEW)
    bl_description = i18n.get_key(i18n.NEW_FILTER_PRESET)
    bl_options = {"REGISTER", "UNDO"}

    is_part_of_instrument: bpy.props.BoolProperty(name="IsPartOfInstrument", options={'HIDDEN'})
    action_index: bpy.props.IntProperty(name="Index", options={'HIDDEN'})
    midi_data_type: bpy.props.IntProperty(name="MidiDataType", options={'HIDDEN'})

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    @staticmethod
    def __copy_to_new_filter(note_action_property, new_filter):
        PropertyUtils.copy_filters(note_action_property.note_filter_groups,
                                   new_filter.note_filter_groups)

    def action_common(self, context):
        note_action_property = PropertyUtils.selected_note_property(midi_data.get_midi_data(self.midi_data_type),
                                                                    self.properties.is_part_of_instrument,
                                                                    self.properties.action_index,
                                                                    context)
        CollectionUtils.add_to_collection(
            context.scene.midi_copier_data_common.filter_presets, i18n.get_key(i18n.PRESET),
            note_action_property, "selected_note_filter_preset",
            update_new_object=lambda new_filter: NLA_MIDI_COPIER_OT_add_note_filter_preset.__copy_to_new_filter(
                note_action_property, new_filter))


class NLA_MIDI_COPIER_OT_save_note_filter_preset(bpy.types.Operator):
    bl_idname = "nla_midi_copier.save_note_filter_preset"
    bl_label = i18n.get_key(i18n.SAVE)
    bl_description = i18n.get_key(i18n.SAVE_FILTER_PRESET)
    bl_options = {"REGISTER", "UNDO"}

    is_part_of_instrument: bpy.props.BoolProperty(name="IsPartOfInstrument", options={'HIDDEN'})
    action_index: bpy.props.IntProperty(name="ActionIndex", options={'HIDDEN'})
    midi_data_type: bpy.props.IntProperty(name="MidiDataType", options={'HIDDEN'})

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        note_action_property = PropertyUtils.selected_note_property(midi_data.get_midi_data(self.midi_data_type),
                                                                    self.properties.is_part_of_instrument,
                                                                    self.properties.action_index,
                                                                    context)
        filter_preset = CollectionUtils.get_selected_object(
            note_action_property.selected_note_filter_preset,
            context.scene.midi_copier_data_common.filter_presets)
        PropertyUtils.copy_filters(note_action_property.note_filter_groups, filter_preset.note_filter_groups)


class NLA_MIDI_COPIER_OT_delete_note_filter_preset(bpy.types.Operator):
    bl_idname = "nla_midi_copier.delete_note_filter_preset"
    bl_label = i18n.get_key(i18n.DELETE_OP)
    bl_description = i18n.get_key(i18n.DELETE_FILTER_PRESET)
    bl_options = {"REGISTER", "UNDO"}

    is_part_of_instrument: bpy.props.BoolProperty(name="IsPartOfInstrument", options={'HIDDEN'})
    action_index: bpy.props.IntProperty(name="Index", options={'HIDDEN'})
    midi_data_type: bpy.props.IntProperty(name="MidiDataType", options={'HIDDEN'})

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        note_action_property = PropertyUtils.selected_note_property(midi_data.get_midi_data(self.midi_data_type),
                                                                    self.properties.is_part_of_instrument,
                                                                    self.properties.action_index,
                                                                    context)
        CollectionUtils.remove_from_collection(context.scene.midi_copier_data_common.filter_presets,
                                               note_action_property, "selected_note_filter_preset")
