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


class GenerateTransitionsOperator(bpy.types.Operator, OperatorUtils.DynamicTooltipOperator):
    bl_idname = "ops.nla_midi_generate_transitions_operator"
    bl_label = "Generate Transitions"
    bl_description = "Generate transitions between selected NLA strips on the active NLA track"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        selected_strip_groups = []
        previous_selected = False
        active_nla_track_strips = context.active_nla_track.strips
        for nla_strip in active_nla_track_strips:
            # treat all transition strips as part of consecutive selection even if not selected
            if nla_strip.select or nla_strip.type == 'TRANSITION':
                if not previous_selected:
                    selected_strip_groups.append([nla_strip])
                else:
                    selected_strip_groups[-1].append(nla_strip)
                previous_selected = True
            else:
                previous_selected = False
        other_tool_property = context.scene.midi_data_property.other_tool_property
        if other_tool_property.replace_transition_strips:
            for nla_strip_group in reversed(selected_strip_groups):
                for nla_strip in reversed(nla_strip_group):
                    if "Transition" in nla_strip.name or nla_strip == 'TRANSITION':
                        active_nla_track_strips.remove(nla_strip)
                        nla_strip_group.remove(nla_strip)

        # TODO handle META strips, or skip them?
        for nla_strip_group in selected_strip_groups:
            previous_strip = None
            for nla_strip in nla_strip_group:
                if nla_strip.action is not None and previous_strip is not None and previous_strip.action is not None:
                    keyframe_properties = other_tool_property.keyframe_properties
                    if other_tool_property.limit_transition_length:
                        ActionUtils.generate_transition_strip(
                            previous_strip, nla_strip, context.active_nla_track,
                            keyframe_properties.interpolation, keyframe_properties.easing,
                            other_tool_property.transition_limit_frames,
                            other_tool_property.transition_placement == "end")
                    else:
                        ActionUtils.generate_transition_strip(
                            previous_strip, nla_strip, context.active_nla_track,
                            keyframe_properties.interpolation, keyframe_properties.easing)
                previous_strip = nla_strip
