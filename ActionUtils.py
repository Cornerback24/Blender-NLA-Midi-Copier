from . import BlenderVersionUtil


def get_action_util_object():
    return ActionUtil() if BlenderVersionUtil.has_slotted_actions() else LegacyActionUtil()


# node trees don't show up in the selector,
# so applying an action is done by selecting the object the node tree belongs to
NODE_TREE_TYPES = {"MATERIAL", "TEXTURE", "WORLD", "SCENE", "LIGHT"}


class ActionUtil:
    def interpolation_has_easing(self, interpolation: str):
        return interpolation not in ("CONSTANT", "LINEAR", "BEZIER")

    def actions_starting_after_frame(self, nla_track, start_after_frame: int):
        index = 0
        nla_strip_count = len(nla_track.strips)
        while index < nla_strip_count:
            if nla_track.strips[index].frame_start > start_after_frame:
                return nla_track.strips[index:]
            index += 1
        return []

    def generate_transition_strip(self, context, strip1, strip2, nla_track, interpolation: str, easing: str,
                                  frame_offset: int = 0, frame_length_limit: int = None, place_at_end: bool = False):
        transition_frame_start = strip1.frame_end
        transition_frame_end = strip2.frame_start
        if transition_frame_end - transition_frame_start <= 0:
            # no space for transition strip
            return
        if frame_length_limit is not None:
            if (transition_frame_end - transition_frame_start) > frame_length_limit:
                transition_frame_offset = min(strip2.frame_start - strip1.frame_end - frame_length_limit, frame_offset)
                if place_at_end:
                    transition_frame_end = transition_frame_end - transition_frame_offset
                    transition_frame_start = transition_frame_end - frame_length_limit
                else:
                    transition_frame_start = transition_frame_start + transition_frame_offset
                    transition_frame_end = transition_frame_start + frame_length_limit
        first_frame_values = self.evaluate_action_at_frame(strip1, transition_frame_start)
        last_frame_values = self.evaluate_action_at_frame(strip2, transition_frame_end)

        fcurves_to_generate = [x for x in first_frame_values.keys() if x in last_frame_values.keys()]
        action_id_type = self.get_id_type(strip1)
        if len(fcurves_to_generate) > 0:
            # Note: 'Transition' is not translated here because Blender does not translate the names of it's generated
            # transition strips
            action = self.new_action(f"{strip1.action.name} Transition", context)
            for fcurve_data in fcurves_to_generate:
                fcurve = self.create_fcurves(action, fcurve_data[0], fcurve_data[1], action_id_type)
                fcurve.keyframe_points.insert(1, first_frame_values[fcurve_data])
                fcurve.keyframe_points.insert(transition_frame_end - transition_frame_start + 1,
                                              last_frame_values[fcurve_data])
                fcurve.keyframe_points[0].interpolation = interpolation
                if self.interpolation_has_easing(interpolation):
                    fcurve.keyframe_points[0].easing = easing

            start_frame_fractional_part = transition_frame_start % 1
            if start_frame_fractional_part > 0:
                strips_to_shift = self.actions_starting_after_frame(nla_track, transition_frame_start)
                self.shift_action_strips(strips_to_shift, 1)
                # api only allows int start frame here, place a frame ahead and then adjust
                nla_strip = nla_track.strips.new(action.name, int(transition_frame_start) + 1, action)
                nla_strip.frame_start = transition_frame_start
                nla_strip.frame_end = transition_frame_end
                self.shift_action_strips(strips_to_shift, -1)
            else:
                nla_track.strips.new(action.name, int(transition_frame_start), action)

    def create_fcurves(self, new_action, data_path, index, id_type):
        if not new_action.layers:
            layer = new_action.layers.new("Layer")
        else:
            layer = new_action.layers[0]
        if not layer.strips:
            action_strip = layer.strips.new(type='KEYFRAME')
        else:
            action_strip = layer.strips[0]
        if not new_action.slots:
            action_slot = new_action.slots.new(name="Transition", id_type=id_type)
        else:
            action_slot = new_action.slots[0]

        # Get the channelbag for this slot, creating it if necessary:
        channelbag = action_strip.channelbag(action_slot, ensure=True)

        fcurve = channelbag.fcurves.new(data_path=data_path, index=index)
        return fcurve

    def evaluate_action_at_frame(self, nla_strip, frame: float):
        """
        :param nla_strip: nla strip
        :param frame: frame to evaluate the action's value at
        :return: { (fcurve_data_path, fcurve_index) : value }
        """
        fcurve_frame = nla_strip.action_frame_end - frame + nla_strip.frame_start if nla_strip.use_reverse else \
            frame - nla_strip.frame_start + nla_strip.action_frame_start
        values = {}
        for fcurve in self.get_action_strip_fcurves(nla_strip):
            values[(fcurve.data_path, fcurve.array_index)] = fcurve.evaluate(fcurve_frame)
        return values

    def get_action_strip_fcurves(self, nla_strip):
        # actions currently have only one layer and one strip
        action_strip = nla_strip.action.layers[0].strips[0]
        channelbag = action_strip.channelbag(nla_strip.action_slot)
        return channelbag.fcurves

    def get_id_type(self, nla_strip):
        return nla_strip.action.slots[0].target_id_type

    def new_action(self, name: str, context):
        return context.blend_data.actions.new(name)

    def shift_action_strips(self, action_strips, shift_amount_frames: float):
        if shift_amount_frames > 0:
            for strip in reversed(action_strips):
                strip.frame_end = strip.frame_end + shift_amount_frames
                strip.frame_start = strip.frame_start + shift_amount_frames
        elif shift_amount_frames < 0:
            for strip in action_strips:
                strip.frame_start = strip.frame_start + shift_amount_frames
                strip.frame_end = strip.frame_end + shift_amount_frames

    def action_length(self, action):
        # return action length (return minimum length of 1 even if the frame range
        # is less than one for an action that only has one keyframe)
        return max(action.frame_range[1] - action.frame_range[0], 1)

    def action_valid_for_id_type(self, id_type: str, action) -> bool:
        for action_slot in action.slots:
            if action_slot.target_id_type == id_type or (
                    action_slot.target_id_type == "NODETREE" and id_type in NODE_TREE_TYPES):
                return True
        return False

    def id_type_from_action(self, action, action_slot=None) -> str:
        if BlenderVersionUtil.has_slotted_actions():
            if action_slot is None:
                action_slot = action.slots[0]
            return action_slot.target_id_type
        else:
            return action.id_root


class LegacyActionUtil(ActionUtil):
    """
    Contains methods for actions before slotted actions were introduced in Blender 4.4.
    """

    def action_valid_for_id_type(self, id_type: str, action) -> bool:
        return action.id_root == id_type or (
                action.id_root == "NODETREE" and id_type in NODE_TREE_TYPES)

    def get_action_strip_fcurves(self, strip):
        return strip.action.fcurves

    def create_fcurves(self, new_action, data_path, index, id_type):
        return new_action.fcurves.new(data_path=data_path, index=index)

    def get_id_type(self, nla_strip):
        return None # not used before slotted actions

