from abc import abstractmethod, ABC

if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PropertyUtils)
else:
    from . import midi_data
    from . import PropertyUtils
import bpy


class AddNoteFilter(bpy.types.Operator):
    bl_idname = "ops.nla_midi_add_note_filter"
    bl_label = "Add Filter"
    bl_description = "Add a filter"
    bl_options = {"REGISTER", "UNDO"}

    is_part_of_instrument: bpy.props.BoolProperty(name="IsPartOfInstrument")
    action_index: bpy.props.IntProperty(name="ActionIndex")
    filter_group_index: bpy.props.IntProperty(name="FilterGroupIndex")
    midi_data_type: bpy.props.IntProperty(name="MidiDataType")

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


class RemoveNoteFilter(bpy.types.Operator):
    bl_idname = "ops.nla_midi_remove_note_filter"
    bl_label = "Remove Filter"
    bl_description = "Remove filter"
    bl_options = {"REGISTER", "UNDO"}

    is_part_of_instrument: bpy.props.BoolProperty(name="IsPartOfInstrument")
    action_index: bpy.props.IntProperty(name="ActionIndex")
    filter_group_index: bpy.props.IntProperty(name="FilterGroupIndex")
    filter_index: bpy.props.IntProperty(name="FilterIndex")
    midi_data_type: bpy.props.IntProperty(name="MidiDataType")

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


class ReorderFilter(bpy.types.Operator):
    bl_idname = "ops.nla_midi_reorder_note_filter"
    bl_label = "Reorder Filter"
    bl_description = "Change filter order"
    bl_options = {"REGISTER", "UNDO"}

    is_part_of_instrument: bpy.props.BoolProperty(name="IsPartOfInstrument")
    action_index: bpy.props.IntProperty(name="ActionIndex")
    filter_group_index: bpy.props.IntProperty(name="FilterGroupIndex")
    filter_index: bpy.props.IntProperty(name="FilterIndex")
    reorder_factor: bpy.props.IntProperty(name="ReorderFactor")
    midi_data_type: bpy.props.IntProperty(name="MidiDataType")

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


class AddNoteFilterGroup(bpy.types.Operator):
    bl_idname = "ops.nla_midi_add_note_filter_group"
    bl_label = "Add Filter Group"
    bl_description = "Add a filter group.\nA filter group is a list of filters to be applied when coping the action. " \
                     "The filters in each group will be applied in the order they are defined. " \
                     "The action is copied to notes that match any of the filter groups"
    bl_options = {"REGISTER", "UNDO"}

    is_part_of_instrument: bpy.props.BoolProperty(name="IsPartOfInstrument")
    action_index: bpy.props.IntProperty(name="Index")
    midi_data_type: bpy.props.IntProperty(name="MidiDataType")

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


class RemoveFilterGroup(bpy.types.Operator):
    bl_idname = "ops.nla_midi_remove_note_filter_group"
    bl_label = "Remove Filter Group"
    bl_description = "Delete Filter Group"
    bl_options = {"REGISTER", "UNDO"}

    is_part_of_instrument: bpy.props.BoolProperty(name="IsPartOfInstrument")
    action_index: bpy.props.IntProperty(name="ActionIndex")
    filter_group_index: bpy.props.IntProperty(name="FilterGroupIndex")
    midi_data_type: bpy.props.IntProperty(name="MidiDataType")

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
