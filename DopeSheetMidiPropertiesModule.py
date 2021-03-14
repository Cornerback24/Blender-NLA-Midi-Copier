if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiPropertiesModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
else:
    from . import midi_data
    from . import MidiPropertiesModule
    from . import NoteFilterImplementations

from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, PointerProperty, CollectionProperty, \
    FloatProperty
from bpy.types import PropertyGroup
from .midi_data import MidiDataType
from .MidiPropertiesModule import MidiPropertyBase, TempoPropertyBase, NoteActionPropertyBase, NoteFilterPropertyBase


class DopeSheetNoteFilterProperty(PropertyGroup, NoteFilterPropertyBase):
    data_type = MidiDataType.DOPESHEET


class DopeSheetNoteFilterGroup(PropertyGroup):
    note_filters: CollectionProperty(type=DopeSheetNoteFilterProperty, name="Note Filters")
    expanded: BoolProperty(name="Expanded", default=True)


class DopeSheetNoteActionProperty(PropertyGroup, NoteActionPropertyBase):
    data_type = MidiDataType.DOPESHEET

    delete_source_keyframes: \
        BoolProperty(name="Delete Source Keyframes",
                     description="Delete the source keyframes after copying",
                     default=False)
    skip_overlaps: \
        BoolProperty(name="Skip Overlaps",
                     description="Skip notes if the first frame would be at or "
                                 "before the last frame of the previous note",
                     default=False)

    sync_length_with_notes: \
        BoolProperty(name="Sync Length with Notes",
                     description="Scale the copied keyframes' spacing so that the length matches the "
                                 "lengths of the notes they are copied to",
                     default=False)

    note_filter_groups: CollectionProperty(type=DopeSheetNoteFilterGroup, name="Note Filter Groups")


class DopeSheetTempoPropertyGroup(PropertyGroup, TempoPropertyBase):
    data_type = MidiDataType.DOPESHEET


class DopeSheetMidiPropertyGroup(MidiPropertyBase, PropertyGroup):
    data_type = MidiDataType.DOPESHEET
    note_action_property: PointerProperty(type=DopeSheetNoteActionProperty)
    tempo_settings: PointerProperty(type=DopeSheetTempoPropertyGroup)
