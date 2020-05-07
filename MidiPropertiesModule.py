if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
else:
    from . import midi_data
    from . import NoteFilterImplementations

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, PointerProperty, CollectionProperty, \
    FloatProperty
from bpy.types import PropertyGroup


def get_all_notes(self, context):
    return midi_data.midi_data.get_all_notes(context)


def get_tracks_list(self, context):
    return midi_data.get_tracks_list(self, context)


def get_notes_list(self, context):
    return midi_data.midi_data.get_notes_list(self, context)


def action_poll(note_action_property, action):
    id_root = midi_data.ID_PROPERTIES_DICTIONARY[note_action_property.id_type][1]
    return action.id_root == id_root or (
            action.id_root == "NODETREE" and id_root in midi_data.note_tree_types)


def on_id_type_updated(note_action_property, context):
    # clear the action since it no longer applies to the selected id type
    note_action_property.action = None


def on_action_updated(note_action_property, context):
    action = note_action_property.action
    # update the action length property to match the actual length of the action
    if action is not None:
        note_action_property.action_length = action.frame_range[1] - action.frame_range[0]


def on_object_updated(note_action_property, context):
    if note_action_property.object is not None:
        # either copy to note_action_property.object or to selected objects, not both
        note_action_property.copy_to_selected_objects = False


def on_copy_to_selected_objects_updated(note_action_property, context):
    if note_action_property.copy_to_selected_objects:
        # either copy to note_action_property.object or to selected objects, not both
        note_action_property.object = None


COMPARISON_ENUM_PROPERTY_ITEMS = [("less_than", "<", "Less than"),
                                  ("less_than_or_equal_to", "<=", "Less than or equal to"),
                                  ("equal_to", "=", "Equal to"),
                                  ("greater_than_or_equal_to", ">=", "Greater than or equal to"),
                                  ("greater_than", ">", "Greater than")]

TIME_UNITS = [("frames", "Frames", "Frames"),
              ("seconds", "Seconds", "Seconds")]


class NoteFilterProperty(PropertyGroup):
    filter_type: EnumProperty(items=NoteFilterImplementations.FILTER_ENUM_PROPERTY_ITEMS, name="Filter Type",
                              description="Filter Type", default="note_pitch_filter")
    comparison_operator: EnumProperty(items=COMPARISON_ENUM_PROPERTY_ITEMS, name="Comparison Operator",
                                      description="Comparison Operator", default="equal_to")
    note_pitch: EnumProperty(items=get_all_notes, name="Pitch", description="Pitch")
    non_negative_int: IntProperty(name="Non Negative Int", description="Non-negative integer", min=0)
    positive_int: IntProperty(name="Positive Int", description="Positive Integer", min=1, default=1)
    positive_int_2: IntProperty(name="Positive Int", description="Positive Integer", min=1, default=1)
    int_0_to_127: IntProperty(name="Integer", description="Integer between 0 and 127, inclusive", min=0, max=127)
    non_negative_number: FloatProperty(name="Non negative number", description="Non negative number", min=0.0)
    time_unit: EnumProperty(items=TIME_UNITS, name="Time unit", description="Time unit", default="frames")


class NoteFilterGroup(PropertyGroup):
    note_filters: CollectionProperty(type=NoteFilterProperty, name="Note Filters")
    expanded: BoolProperty(name="Expanded", default=True)


class NoteActionProperty(PropertyGroup):
    id_type: EnumProperty(
        items=sorted([(x, x, x) for x in midi_data.ID_PROPERTIES_DICTIONARY.keys()], key=lambda x: x[0]),
        name="Type", description="Type of object to apply the action to", default="Object", update=on_id_type_updated)

    action: PointerProperty(type=bpy.types.Action, name="Action", description="The action to create action strips from",
                            poll=action_poll, update=on_action_updated)

    midi_frame_offset: \
        IntProperty(name="Frame Offset",
                    description="Frame offset when copying strips")

    delete_source_action_strip: \
        BoolProperty(name="Delete Source Action",
                     description="Delete the source action after copying",
                     default=False)
    delete_source_track: \
        BoolProperty(name="Delete Source Track",
                     description="Delete the track containing the source action if it is empty",
                     default=False)

    nla_track_name: \
        StringProperty(name="Nla Track",
                       description="Name of the NLA Track that action strips will be placed on.\n " +
                                   "A track name will be automatically generated if this is blank.")

    duplicate_object_on_overlap: \
        BoolProperty(name="Duplicate Object on Overlap",
                     description="Copy the action to a duplicated object if it overlaps another action",
                     default=False)

    sync_length_with_notes: \
        BoolProperty(name="Sync Length with Notes",
                     description="Scale the copied NLA strips so that their lengths match the lengths of the notes "
                                 "they are copied to",
                     default=False)

    add_filters: \
        BoolProperty(name="Add filters",
                     description="Add filters to exclude notes",
                     default=False)

    filters_expanded: BoolProperty(name="Expanded", default=True)

    note_filter_groups: CollectionProperty(type=NoteFilterGroup, name="Note Filter Groups")

    copy_to_selected_objects: \
        BoolProperty(name="Copy Action to Selected Objects",
                     description="Copy the action to all selected objects.",
                     default=False, update=on_copy_to_selected_objects_updated)

    action_length: \
        IntProperty(name="Action Length (Frames)",
                    description="Length of the action, used to determine if the next action overlaps.\n" +
                                "This will be ignored if it is shorter than the actual length of the action")

    scale_factor: \
        FloatProperty(name="Scale Factor",
                      description="Scale factor for scaling to the note's length. "
                                  "For example, a scale factor of 1 will scale to the note's length, "
                                  "a scale factor of 2 will scale to twice the note's length, " +
                                  "and a scale factor of 0.5 will scale to half the note's length",
                      min=0.0000001, max=1000000, soft_min=0.0000001, soft_max=1000000, default=1)

    # used for display in the instruments panel
    expanded: BoolProperty(name="Expanded", default=True)

    armature: PointerProperty(type=bpy.types.Armature, name="Armature", description="The armature to animate")
    camera: PointerProperty(type=bpy.types.Camera, name="Camera", description="The camera to animate")
    cachefile: PointerProperty(type=bpy.types.CacheFile, name="Cache File", description="The cache file to animate")
    curve: PointerProperty(type=bpy.types.Curve, name="Curve", description="The curve to animate")
    greasepencil: PointerProperty(type=bpy.types.GreasePencil, name="Grease Pencil",
                                  description="The grease pencil to animate")
    key: PointerProperty(type=bpy.types.Key, name="Key", description="The key to animate")
    lattice: PointerProperty(type=bpy.types.Lattice, name="Lattice", description="The lattice to animate")
    light: PointerProperty(type=bpy.types.Light, name="Light", description="The light to animate")
    mask: PointerProperty(type=bpy.types.Mask, name="Mask", description="The mask to animate")
    material: PointerProperty(type=bpy.types.Material, name="Material", description="The material to animate")
    meta: PointerProperty(type=bpy.types.MetaBall, name="MetaBall", description="The meta to animate")
    mesh: PointerProperty(type=bpy.types.Mesh, name="Mesh", description="The mesh to animate")
    movieclip: PointerProperty(type=bpy.types.MovieClip, name="Movie Clip", description="The movie clip to animate")
    nodetree: PointerProperty(type=bpy.types.NodeTree, name="Node Tree", description="The node tree to animate")
    object: PointerProperty(type=bpy.types.Object, name="Object", description="The object to animate",
                            update=on_object_updated)
    light_probe: PointerProperty(type=bpy.types.LightProbe, name="Light  Probe",
                                 description="The light_probe to animate")
    scene: PointerProperty(type=bpy.types.Scene, name="Scene", description="The scene to animate")
    speaker: PointerProperty(type=bpy.types.Speaker, name="Speaker", description="The speaker to animate")
    texture: PointerProperty(type=bpy.types.Texture, name="Texture", description="The texture to animate")
    world: PointerProperty(type=bpy.types.World, name="World", description="The world to animate")


class InstrumentNoteProperty(PropertyGroup):
    name: StringProperty(name="Name")
    note_id: IntProperty(name="Note")
    actions: CollectionProperty(type=NoteActionProperty, name="Actions")


TRANSPOSE_FILTER_ITEMS = \
    [("no_transpose", "Do not transpose", "Do not transpose"),
     ("transpose_if_possible_leave_all_inclusive", "Transpose if possible except all-inclusive",
      "Transpose filters if possible. Does not transpose filters that can't be transposed due to range constraints. "
      "Does not transpose filters than include every pitch"),
     ("transpose_if_possible", "Transpose if possible",
      "Transpose filters if possible. Does not transpose filters that can't be transposed due to range constraints"),
     ("transpose_all_leave_all_inclusive", "Transpose all except all-inclusive",
      "Transpose all filters except for filters than include every pitch"),
     ("transpose_all", "Transpose all", "Transpose all filters")]


class InstrumentProperty(PropertyGroup):
    name: StringProperty(name="Name")
    default_midi_frame_offset: IntProperty(name="Default Frame Offset",
                                           description="Frame offset when copying strips")
    notes: CollectionProperty(type=InstrumentNoteProperty, name="Notes")
    selected_note_id: EnumProperty(items=midi_data.get_instrument_notes,
                                   name="Note", description="Note")

    selected_midi_track: EnumProperty(items=get_tracks_list,
                                      name="Track",
                                      description="Selected Midi Track")
    # properties for drawing the panel
    properties_expanded: BoolProperty(name="Expanded", default=True)
    notes_expanded: BoolProperty(name="Expanded", default=True)
    animate_expanded: BoolProperty(name="Expanded", default=True)
    transpose_filters: EnumProperty(items=TRANSPOSE_FILTER_ITEMS, name="Transpose Filters",
                                    description="Set how pitch filters will be transposed",
                                    default="transpose_all_leave_all_inclusive")


def get_midi_file_name(self):
    if "midi_file" in self:
        return self["midi_file"]
    return ""


middle_c_options = [("C3", "C3", "C3"), ("C4", "C4", "C4"), ("C5", "C5", "C5")]


def update_middle_c(self, context):
    midi_data.midi_data.middle_c_id = self.middle_c_note


class MidiPropertyGroup(PropertyGroup):
    # defining get= (and not set=) disables editing in the UI
    midi_file: StringProperty(name="Midi File", description="Select Midi File", get=get_midi_file_name)
    notes_list: EnumProperty(items=get_notes_list,
                             name="Note",
                             description="Note")
    track_list: EnumProperty(items=get_tracks_list,
                             name="Track",
                             description="Selected Midi Track")
    note_action_property: PointerProperty(type=NoteActionProperty)
    midi_frame_start: \
        IntProperty(name="First Frame",
                    description="The frame corresponding to the beginning of the midi file",
                    default=1)

    instruments: CollectionProperty(type=InstrumentProperty, name="Instruments")
    selected_instrument_id: EnumProperty(items=midi_data.get_instruments, name="Instrument",
                                         description="Select an instrument")
    middle_c_note: EnumProperty(items=middle_c_options,
                                name="Middle C", description="The note corresponding to middle C (midi note 60)",
                                default="C4", update=update_middle_c)
