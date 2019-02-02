if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NLAMidiCopierModule)
else:
    from . import midi_data
    # noinspection PyUnresolvedReferences
    from . import NLAMidiCopierModule

import bpy
from .NLAMidiCopierModule import NLAMidiCopier
from . import midi_data
from bpy.props import EnumProperty


class MidiFileSelector(bpy.types.Operator):
    bl_idname = "ops.midi_file_selector"
    bl_label = "Midi File Selector"
    # noinspection PyArgumentList
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.midi_data_property.midi_file = self.filepath
        try:
            midi_data.update_midi_file(self.filepath, True)
        except Exception as e:
            self.report({"WARNING"}, "Could not load midi file: " + str(e))
            context.scene.midi_data_property.midi_file = ""
            midi_data.update_midi_file(None, False)

        return {'FINISHED'}

    # noinspection PyUnusedLocal
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MidiPanel(bpy.types.Panel):
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_category = "Midi"
    bl_label = "Blender NLA Midi"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator(MidiFileSelector.bl_idname, text="Choose midi file", icon='FILE_FOLDER')

        midi_data_property = context.scene.midi_data_property
        midi_file = midi_data_property.midi_file
        if midi_data_property.midi_file:
            try:
                midi_data.update_midi_file(midi_data_property.midi_file, False)
                col.prop(midi_data_property, "midi_file")

                col.prop(midi_data_property, "track_list")
                col.prop(midi_data_property, "notes_list")
            except Exception as e:
                print("Could not load midi file: " + str(e))
                midi_data.update_midi_file(None, False)

        note_action_property = midi_data_property.note_action_property
        col.prop(note_action_property, "id_type")
        if note_action_property.id_type is not None:
            col.prop(note_action_property, midi_data.ID_PROPERTIES_DICTIONARY[note_action_property.id_type][0])
            col.prop(note_action_property, "action")

        self.layout.separator()

        col = self.layout.column(align=True)
        col.enabled = note_action_property.id_type == "Object"
        col.prop(note_action_property, "copy_to_selected_objects")
        col.prop(note_action_property, "duplicate_object_on_overlap")
        col = self.layout.column(align=True)
        col.prop(note_action_property, "nla_track_name")
        col.prop(midi_data_property, "midi_frame_start")
        col.prop(note_action_property, "midi_frame_offset")
        if note_action_property.action is not None:
            col.prop(note_action_property, "action_length")

        self.layout.separator()

        # col.prop(note_action_property, "copy_to_new_track") TODO support coping to existing tracks ?

        if midi_file:
            col = self.layout.column(align=True)
            col.enabled = note_action_property.action is not None
            col.operator(NLAMidiCopier.bl_idname, icon='FILE_SOUND')


class OneClickMidiPanel(bpy.types.Panel):
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_category = "Midi"
    bl_label = "One Click NLA Midi"

    def draw(self, context):
        temp = 0  # TODO implement panel, allow for defining actions for entire instrument
