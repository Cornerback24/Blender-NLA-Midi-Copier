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

from .NLAMidiCopierModule import NLAMidiCopier
from . import midi_data
import bpy


class MidiFileSelector(bpy.types.Operator):
    bl_idname = "ops.midi_file_selector"
    bl_label = "Midi File Selector"
    # noinspection PyArgumentList
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.midi_file = self.filepath
        try:
            midi_data.update_midi_file(self.filepath, True)
        except Exception as e:
            self.report({"WARNING"}, "Could not load midi file: " + str(e))
            context.scene.midi_file = ""
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
        col.operator(MidiFileSelector.bl_idname, "Choose midi file", icon='FILESEL')

        if context.scene.midi_file:
            try:
                midi_data.update_midi_file(context.scene.midi_file, False)
                col.prop(context.scene, "midi_file")

                col.prop(context.scene, "track_list")
                col.prop(context.scene, "notes_list")
                col.operator(NLAMidiCopier.bl_idname, icon='FILE_SOUND')
            except Exception as e:
                print("Could not load midi file: " + str(e))
                midi_data.update_midi_file(None, False)

        self.layout.separator()

        col = self.layout.column(align=True)
        col.prop(context.scene, "midi_frame_start")
        col.prop(context.scene, "midi_frame_offset")

        self.layout.separator()

        col.prop(context.scene, "copy_to_new_track")
        col.prop(context.scene, "delete_source_action_strip")
        col.prop(context.scene, "delete_source_track")
        col.prop(context.scene, "midi_linked_duplicate_property")
