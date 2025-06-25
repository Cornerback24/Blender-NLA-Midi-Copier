from .i18n import i18n

import bpy


class MidiCopierPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    show_nla_midi_other_tools_panel: bpy.props.BoolProperty(
        name=i18n.get_key(i18n.SHOW_OTHER_TOOLS_PANEL),
        description=i18n.get_key(i18n.SHOW_OTHER_TOOLS_PANEL_IF_ENABLED),
        default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_nla_midi_other_tools_panel")
