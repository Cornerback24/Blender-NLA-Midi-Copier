if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    # noinspection PyUnresolvedReferences
    from . import midi_data
    from .i18n import i18n

import bpy
import traceback


def load_midi_file(operator, context, data_type: int, filepath: str):
    loaded_midi_data = midi_data.get_midi_data(data_type)
    midi_data_property = midi_data.get_midi_data_property(data_type, context)
    # need to set with array notation because the property is defined to be read-only
    midi_data_property["midi_file"] = filepath
    try:
        loaded_midi_data.update_midi_file(filepath, True, context)
    except Exception as e:
        # noinspection PyArgumentList,PyUnresolvedReferences
        operator.report({"WARNING"}, i18n.concat(i18n.get_text(i18n.COULD_NOT_LOAD_MIDI_FILE), str(e)))
        print(traceback.format_exc())
        midi_data_property["midi_file"] = ""
        loaded_midi_data.update_midi_file(None, False, context)


class CopyMidiFileData(bpy.types.Operator):
    """
    Operator to load midi file data form another view
    (load the midi file from the NLA editor into the graph editor, for example)
    """

    bl_idname = "ops.midi_file_copy_data"
    bl_label = i18n.get_key(i18n.COPY_MIDI_FILE_DATA_OP)
    bl_description = i18n.get_key(i18n.COPY_MIDI_FILE_DATA)
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    copy_from_data_type: bpy.props.IntProperty(name="From", options={'HIDDEN'})
    copy_to_data_type: bpy.props.IntProperty(name="To", options={'HIDDEN'})
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
        midi_data_property_from = midi_data.get_midi_data_property(self.copy_from_data_type, context)
        load_midi_file(self, context, self.copy_to_data_type, midi_data_property_from.midi_file)

        midi_data_property_to = midi_data.get_midi_data_property(self.properties.copy_to_data_type, context)
        midi_data_property_to.midi_frame_start = midi_data_property_from.midi_frame_start
        midi_data_property_to.middle_c_note = midi_data_property_from.middle_c_note

        tempo_settings_from = midi_data_property_from.tempo_settings
        tempo_settings_to = midi_data_property_to.tempo_settings
        tempo_settings_to.use_file_tempo = tempo_settings_from.use_file_tempo
        tempo_settings_to.beats_per_minute = tempo_settings_from.beats_per_minute
        tempo_settings_to.use_file_ticks_per_beat = tempo_settings_from.use_file_ticks_per_beat
        tempo_settings_to.ticks_per_beat = tempo_settings_from.ticks_per_beat

        midi_track_properties_from = midi_data_property_from.midi_track_properties
        midi_track_properties_to = midi_data_property_to.midi_track_properties
        midi_track_properties_to.clear()
        for midi_track_property_from in midi_track_properties_from:
            midi_track_property_to = midi_track_properties_to.add()
            midi_track_property_to.midi_data_type = self.copy_to_data_type
            midi_track_property_to.midi_track_name = midi_track_property_from.midi_track_name
            midi_track_property_to.displayed_track_name = midi_track_property_from.displayed_track_name

    @staticmethod
    def compare_midi_file_data(context, data_type_1, data_type_2) -> bool:
        midi_data_property_1 = midi_data.get_midi_data_property(data_type_1, context)
        midi_data_property_2 = midi_data.get_midi_data_property(data_type_2, context)

        if midi_data_property_1.midi_file != midi_data_property_2.midi_file or \
                midi_data_property_1.midi_frame_start != midi_data_property_2.midi_frame_start or \
                midi_data_property_1.middle_c_note != midi_data_property_2.middle_c_note:
            return False

        tempo_settings_1 = midi_data_property_1.tempo_settings
        tempo_settings_2 = midi_data_property_2.tempo_settings
        if tempo_settings_1.use_file_tempo != tempo_settings_2.use_file_tempo or \
                tempo_settings_1.beats_per_minute != tempo_settings_2.beats_per_minute or \
                tempo_settings_1.use_file_ticks_per_beat != tempo_settings_2.use_file_ticks_per_beat or \
                tempo_settings_1.ticks_per_beat != tempo_settings_2.ticks_per_beat:
            return False

        midi_track_properties_1 = midi_data_property_1.midi_track_properties
        midi_track_properties_2 = midi_data_property_2.midi_track_properties
        if len(midi_track_properties_1) != len(midi_track_properties_2):
            return False
        for (midi_track_property_1, midi_track_property_2) in zip(midi_track_properties_1, midi_track_properties_2):
            if midi_track_property_1.midi_track_name != midi_track_property_2.midi_track_name or \
                    midi_track_property_1.displayed_track_name != midi_track_property_2.displayed_track_name:
                return False
        return True


class DynamicTooltipOperator:
    tooltip: bpy.props.StringProperty(options={'HIDDEN'})

    @classmethod
    def description(cls, context, properties):
        return properties.tooltip if properties.tooltip else cls.bl_description
