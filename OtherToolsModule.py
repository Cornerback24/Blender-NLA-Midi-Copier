if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(OperatorUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(ActionUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from . import OperatorUtils
    from . import ActionUtils
    from .i18n import i18n

import bpy
import re


def is_transition(nla_strip):
    return nla_strip.type == 'TRANSITION' or re.fullmatch(r".*Transition(.[0-9]*)?", nla_strip.name)


class GenerateTransitionsOperator(bpy.types.Operator, OperatorUtils.DynamicTooltipOperator):
    bl_idname = "ops.nla_midi_generate_transitions_operator"
    bl_label = i18n.get_key(i18n.GENERATE_TRANSITIONS)
    bl_description = i18n.get_key(i18n.GENERATE_TRANSITIONS_DESCRIPTION)
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    @staticmethod
    def selected_nla_strip_groups(context):
        selected_strip_groups = []
        previous_selected = False
        active_nla_track_strips = context.active_nla_track.strips
        for nla_strip in active_nla_track_strips:
            if nla_strip.select:
                if not previous_selected:
                    selected_strip_groups.append([nla_strip])
                else:
                    selected_strip_groups[-1].append(nla_strip)
                previous_selected = True
            else:
                previous_selected = False
        return active_nla_track_strips, selected_strip_groups

    @staticmethod
    def delete_transition_strips(active_nla_track_strips, selected_strip_groups):
        for nla_strip_group in reversed(selected_strip_groups):
            for nla_strip in reversed(nla_strip_group):
                if is_transition(nla_strip):
                    active_nla_track_strips.remove(nla_strip)
                    nla_strip_group.remove(nla_strip)

    def action_common(self, context):
        active_nla_track_strips, selected_strip_groups = GenerateTransitionsOperator.selected_nla_strip_groups(context)
        other_tool_property = context.scene.midi_data_property.other_tool_property
        if other_tool_property.replace_transition_strips:
            GenerateTransitionsOperator.delete_transition_strips(active_nla_track_strips, selected_strip_groups)

        # TODO handle META strips
        for nla_strip_group in selected_strip_groups:
            previous_strip = None
            for nla_strip in nla_strip_group:
                if nla_strip.action is not None and previous_strip is not None and previous_strip.action is not None:
                    keyframe_properties = other_tool_property.keyframe_properties
                    if other_tool_property.limit_transition_length:
                        ActionUtils.generate_transition_strip(
                            context, previous_strip, nla_strip, context.active_nla_track,
                            keyframe_properties.interpolation, keyframe_properties.easing,
                            other_tool_property.transition_offset_frames, other_tool_property.transition_limit_frames,
                            other_tool_property.transition_placement == "end")
                    else:
                        ActionUtils.generate_transition_strip(
                            context, previous_strip, nla_strip, context.active_nla_track,
                            keyframe_properties.interpolation, keyframe_properties.easing)
                previous_strip = nla_strip


class DeleteTransitionsOperator(bpy.types.Operator, OperatorUtils.DynamicTooltipOperator):
    bl_idname = "ops.nla_midi_delete_transitions_operator"
    bl_label = i18n.get_key(i18n.DELETE_TRANSITIONS_OP)
    bl_description = i18n.get_key(i18n.DELETE_TRANSITIONS_DESCRIPTIONS)
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        GenerateTransitionsOperator.delete_transition_strips(
            *GenerateTransitionsOperator.selected_nla_strip_groups(context))
