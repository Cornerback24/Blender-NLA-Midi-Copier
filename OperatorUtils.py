if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
else:
    # noinspection PyUnresolvedReferences
    from . import midi_data

import bpy


def load_midi_file(operator, context, data_type, filepath):
    loaded_midi_data = midi_data.get_midi_data(data_type)
    midi_data_property = midi_data.get_midi_data_property(data_type, context)
    midi_data_property["midi_file"] = filepath
    try:
        loaded_midi_data.update_midi_file(filepath, True, context)
    except Exception as e:
        # noinspection PyArgumentList,PyUnresolvedReferences
        operator.report({"WARNING"}, "Could not load midi file: " + str(e))
        midi_data_property["midi_file"] = ""
        loaded_midi_data.update_midi_file(None, False, context)


class CopyMidiFileData(bpy.types.Operator):
    # Operator to load midi file data form another view
    # (load the midi file from the NLA editor into the graph editor, for example)
    bl_idname = "ops.midi_file_copy_data"
    bl_label = "Copy Midi file data"
    bl_description = "Copy midi file data"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    copy_from_data_type: bpy.props.IntProperty(name="From")
    copy_to_data_type: bpy.props.IntProperty(name="To")
    tooltip: bpy.props.StringProperty(options={'HIDDEN'})

    @classmethod
    def description(cls, context, properties):
        return properties.tooltip if properties.tooltip else cls.bl_description

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        midi_data_property_from = midi_data.get_midi_data_property(self.properties.copy_from_data_type, context)
        load_midi_file(self, context, self.properties.copy_to_data_type, midi_data_property_from.midi_file)

        midi_data_property_to = midi_data.get_midi_data_property(self.properties.copy_to_data_type, context)
        midi_data_property_to.midi_frame_start = midi_data_property_from.midi_frame_start
        midi_data_property_to.middle_c_note = midi_data_property_from.middle_c_note

        tempo_settings_from = midi_data_property_from.tempo_settings
        tempo_settings_to = midi_data_property_to.tempo_settings
        tempo_settings_to.use_file_tempo = tempo_settings_from.use_file_tempo
        tempo_settings_to.beats_per_minute = tempo_settings_from.beats_per_minute
        tempo_settings_to.use_file_ticks_per_beat = tempo_settings_from.use_file_ticks_per_beat
        tempo_settings_to.ticks_per_beat = tempo_settings_from.ticks_per_beat
        tempo_settings_to.ticks_per_beat = tempo_settings_from.ticks_per_beat


class DynamicTooltipOperator:
    tooltip: bpy.props.StringProperty(options={'HIDDEN'})

    @classmethod
    def description(cls, context, properties):
        return properties.tooltip if properties.tooltip else cls.bl_description
