# Module for maintaining compatibility with previous versions of the addon
import bpy

compatibility_updates_complete = True  # if on load compatibility updates have completed


def all_note_action_properties(scene):
    """
    :param scene: blender scene
    :return: list of all NoteActionProperty
    """
    note_action_properties = [scene.midi_data_property.note_action_property]
    for instrument in scene.midi_data_property.instruments:
        for instrument_note in instrument.notes:
            for note_action_property in instrument_note.actions:
                note_action_properties.append(note_action_property)
    return note_action_properties


def duplicate_object_checkbox_to_dropdown(scene):
    """
    Duplicate on Overlap Checkbox was removed and Blending of "None (skip overlaps)" removed. Both replaced by the
    new Overlap dropdown.
    Updates the new Overlap dropdown to match.
    :param scene: blender scene
    """
    for note_action_property in all_note_action_properties(scene):
        if note_action_property.duplicate_object_on_overlap:
            note_action_property.on_overlap = "DUPLICATE_OBJECT"
        elif note_action_property.blend_mode == "None":
            note_action_property.on_overlap = "SKIP"
        else:
            note_action_property.on_overlap = "BLEND"

        if note_action_property.blend_mode == "None":  # Blend mode None no longer used
            note_action_property.blend_mode = "REPLACE"


# (from, to, update function)
COMPATIBILITY_UPDATES = [((0, 11, 0,), (0, 12, 0), duplicate_object_checkbox_to_dropdown)]


def should_run_updates(scene):
    # don't run updates on scenes that don't have data that needs update
    return scene.midi_data_property.midi_file is not None or \
           scene.dope_sheet_midi_data_property.midi_file is not None or \
           scene.graph_editor_midi_data_property.midi_file is not None or \
           len(scene.midi_data_property.instruments) > 0


def run_compatibility_updates(current_version):
    # find the scene with the highest version number, this is the previous addon version
    previous_version = (0, 0, 0)
    for scene in bpy.data.scenes:
        scene_version_property = scene.midi_copier_version
        scene_previous_version = (scene_version_property.major,
                                  scene_version_property.minor, scene_version_property.revision)
        if scene_previous_version > previous_version:
            previous_version = scene_previous_version
    for scene in bpy.data.scenes:
        if should_run_updates(scene):
            for update in COMPATIBILITY_UPDATES:
                if previous_version <= update[0] and current_version >= update[1]:
                    update[2](scene)
