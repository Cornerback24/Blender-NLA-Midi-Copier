# Module for maintaining compatibility with previous versions of the addon
import bpy

compatibility_updates_complete = True  # if on load compatibility updates have completed


def all_note_action_properties(scene):
    """
    :param scene: blender scene
    :return: list of all NoteActionProperty
    """
    note_action_properties = [
        scene.nla_midi_copier_main_property_group.nla_editor_midi_data_property.note_action_property]
    for instrument in scene.nla_midi_copier_main_property_group.nla_editor_midi_data_property.instruments:
        for instrument_note in instrument.notes:
            for note_action_property in instrument_note.actions:
                note_action_properties.append(note_action_property)
    return note_action_properties


# list of (from version, to version, update function), such as ((0.1.0), (0,2,0), update_function)
# the update takes one parameter which is the scene and is run on all scenes
COMPATIBILITY_UPDATES = []


def should_run_updates(scene):
    # don't run updates on scenes that don't have data that needs update
    return scene.nla_midi_copier_main_property_group.nla_editor_midi_data_property.midi_file is not None or \
        scene.nla_midi_copier_main_property_group.dope_sheet_midi_data_property.midi_file is not None or \
        scene.nla_midi_copier_main_property_group.graph_editor_midi_data_property.midi_file is not None or \
        len(scene.nla_midi_copier_main_property_group.nla_editor_midi_data_property.instruments) > 0


def run_compatibility_updates(current_version):
    # find the scene with the highest version number, this is the previous addon version
    previous_version = (0, 0, 0)
    for scene in bpy.data.scenes:
        scene_version_property = scene.nla_midi_copier_main_property_group.midi_copier_version
        scene_previous_version = (scene_version_property.major,
                                  scene_version_property.minor, scene_version_property.revision)
        if scene_previous_version > previous_version:
            previous_version = scene_previous_version
    for scene in bpy.data.scenes:
        if should_run_updates(scene):
            for update in COMPATIBILITY_UPDATES:
                if previous_version <= update[0] and current_version >= update[1]:
                    update[2](scene)
