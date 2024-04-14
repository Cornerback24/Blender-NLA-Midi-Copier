if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiPropertiesModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from . import midi_data
    from . import MidiPropertiesModule
    from . import NoteFilterImplementations
    from .i18n import i18n

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, PointerProperty, CollectionProperty, \
    FloatProperty
from bpy.types import PropertyGroup
from .midi_data import MidiDataType
from .MidiPropertiesModule import MidiPropertyBase, TempoPropertyBase, NoteActionPropertyBase, NoteFilterPropertyBase, \
    NoteFilterGroupPropertyBase


class DopeSheetNoteFilterProperty(PropertyGroup, NoteFilterPropertyBase):
    data_type = MidiDataType.DOPESHEET


class DopeSheetNoteFilterGroup(PropertyGroup, NoteFilterGroupPropertyBase):
    note_filters = CollectionProperty(type=DopeSheetNoteFilterProperty, name=i18n.get_key(i18n.NOTE_FILTERS))


class DopeSheetNoteActionProperty(PropertyGroup, NoteActionPropertyBase):
    data_type = MidiDataType.DOPESHEET

    delete_source_keyframes = \
        BoolProperty(name=i18n.get_key(i18n.DELETE_SOURCE_KEYFRAMES),
                     description=i18n.get_key(i18n.DELETE_SOURCE_KEYFRAMES_DESCRIPTION),
                     default=False)
    skip_overlaps = \
        BoolProperty(name=i18n.get_key(i18n.SKIP_OVERLAPS),
                     description=i18n.get_key(i18n.GREASE_PENCIL_SKIP_OVERLAPS_DESCRIPTION),
                     default=False)

    sync_length_with_notes = \
        BoolProperty(name=i18n.get_key(i18n.SYNC_LENGTH_WITH_NOTES),
                     description=i18n.get_key(i18n.GREASE_PENCIL_SYNC_LENGTH_DESCRIPTION),
                     default=False)

    note_filter_groups = CollectionProperty(type=DopeSheetNoteFilterGroup, name=i18n.get_key(i18n.NOTE_FILTER_GROUPS))


class DopeSheetTempoPropertyGroup(PropertyGroup, TempoPropertyBase):
    data_type = MidiDataType.DOPESHEET


class DopeSheetMidiPropertyGroup(MidiPropertyBase, PropertyGroup):
    data_type = MidiDataType.DOPESHEET
    note_action_property = PointerProperty(type=DopeSheetNoteActionProperty)
    tempo_settings = PointerProperty(type=DopeSheetTempoPropertyGroup)
