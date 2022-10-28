if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from .i18n import i18n

import bpy
from . import addon_updater_ops


class MidiCopierPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    show_nla_midi_other_tools_panel: bpy.props.BoolProperty(
        name=i18n.get_key(i18n.SHOW_OTHER_TOOLS_PANEL),
        description=i18n.get_key(i18n.SHOW_OTHER_TOOLS_PANEL_IF_ENABLED),
        default=True)

    # addon updater preferences
    auto_check_update: bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False)

    updater_interval_months: bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0)

    updater_interval_days: bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=1,
        min=0,
        max=31)

    updater_interval_hours: bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23)

    updater_interval_minutes: bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_nla_midi_other_tools_panel")
        addon_updater_ops.update_settings_ui(self, context)
