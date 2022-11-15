import bpy


def interpolation_has_easing(interpolation: str):
    return interpolation not in ("CONSTANT", "LINEAR", "BEZIER")


def actions_starting_after_frame(nla_track, start_after_frame: int):
    index = 0
    nla_strip_count = len(nla_track.strips)
    while index < nla_strip_count:
        if nla_track.strips[index].frame_start > start_after_frame:
            return nla_track.strips[index:]
        index += 1
    return []


def generate_transition_strip(context, strip1, strip2, nla_track, interpolation: str, easing: str,
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
    first_frame_values = evaluate_action_at_frame(strip1, transition_frame_start)
    last_frame_values = evaluate_action_at_frame(strip2, transition_frame_end)

    fcurves_to_generate = [x for x in first_frame_values.keys() if x in last_frame_values.keys()]
    if len(fcurves_to_generate) > 0:
        # Note: 'Transition' is not translated here because Blender does not translate the names of it's generated
        # transition strips
        action = new_action(f"{strip1.action.name} Transition", context)
        for fcurve_data in fcurves_to_generate:
            fcurve = action.fcurves.new(fcurve_data[0], index=fcurve_data[1])
            fcurve.keyframe_points.insert(1, first_frame_values[fcurve_data])
            fcurve.keyframe_points.insert(transition_frame_end - transition_frame_start + 1,
                                          last_frame_values[fcurve_data])
            fcurve.keyframe_points[0].interpolation = interpolation
            if interpolation_has_easing(interpolation):
                fcurve.keyframe_points[0].easing = easing

        start_frame_fractional_part = transition_frame_start % 1
        if start_frame_fractional_part > 0:
            strips_to_shift = actions_starting_after_frame(nla_track, transition_frame_start)
            shift_action_strips(strips_to_shift, 1)
            # api only allows int start frame here, place a frame ahead and then adjust
            nla_strip = nla_track.strips.new(action.name, int(transition_frame_start) + 1, action)
            nla_strip.frame_start = transition_frame_start
            nla_strip.frame_end = transition_frame_end
            shift_action_strips(strips_to_shift, -1)
        else:
            nla_track.strips.new(action.name, int(transition_frame_start), action)


def evaluate_action_at_frame(strip, frame: float):
    """
    :param strip: nla strip
    :return: { (fcurve_data_path, fcurve_index) : value }
    """
    fcurve_frame = strip.action_frame_end - frame + strip.frame_start if strip.use_reverse else \
        frame - strip.frame_start + strip.action_frame_start
    values = {}
    for fcurve in strip.action.fcurves:
        values[(fcurve.data_path, fcurve.array_index)] = fcurve.evaluate(fcurve_frame)
    return values


def new_action(name: str, context):
    return context.blend_data.actions.new(name)


def shift_action_strips(action_strips, shift_amount_frames: float):
    if shift_amount_frames > 0:
        for strip in reversed(action_strips):
            strip.frame_end = strip.frame_end + shift_amount_frames
            strip.frame_start = strip.frame_start + shift_amount_frames
    elif shift_amount_frames < 0:
        for strip in action_strips:
            strip.frame_start = strip.frame_start + shift_amount_frames
            strip.frame_end = strip.frame_end + shift_amount_frames
