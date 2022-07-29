import bpy


def operator(string):
    return "Operator", string


def get_key(i18n_data):
    return i18n_data if isinstance(i18n_data, str) else i18n_data[1]


def get_label(key):
    return bpy.app.translations.pgettext_iface(key) + ":"


ACTION = "Action"
ACTION_LENGTH_FRAMES = "Action Length "
CHOOSE_MIDI_FILE = operator("Choose midi file")
COPY_ACTION_TO_SELECTED_OBJECTS = "Copy Action to Selected Objects"
COPY_TO_SELECTED_OBJECTS_DESCRIPTION = "Copy the action to all selected objects."
TYPE = "Type"
TYPE_DESCRIPTION = "Type of object to apply the action to"
