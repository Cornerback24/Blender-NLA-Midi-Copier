if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PitchUtils)
else:
    from . import midi_data
    from . import NoteFilterImplementations
    from . import PitchUtils

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, PointerProperty, CollectionProperty, \
    FloatProperty
from bpy.types import PropertyGroup


def get_all_notes(self, context):
    return midi_data.midi_data.get_all_notes(context)


def get_all_notes_for_pitch_filter(self, context):
    return midi_data.midi_data.get_all_notes(context, True)


def get_tracks_list(self, context):
    return midi_data.get_tracks_list(self, context)


def get_notes_list(self, context):
    return midi_data.midi_data.get_notes_list(self, context)


def action_poll(note_action_property, action):
    id_root = midi_data.ID_PROPERTIES_DICTIONARY[note_action_property.id_type][1]
    return action.id_root == id_root or (
            action.id_root == "NODETREE" and id_root in midi_data.node_tree_types)


def on_id_type_updated(note_action_property, context):
    # clear the action since it no longer applies to the selected id type
    note_action_property.action = None
    if note_action_property.copy_to_selected_objects and \
            not midi_data.can_resolve_data_from_selected_objects(note_action_property.id_type):
        # copy to selected objects only works if the id_type corresponds to an object type
        note_action_property.copy_to_selected_objects = False
    # copy along path only works if the id_type corresponds to an object type
    if context.scene.midi_data_property.bulk_copy_property.copy_along_path and \
            not midi_data.can_resolve_data_from_selected_objects(note_action_property.id_type):
        context.scene.midi_data_property.bulk_copy_property.copy_along_path = False


def on_action_updated(note_action_property, context):
    action = note_action_property.action
    # update the action length property to match the actual length of the action
    if action is not None:
        note_action_property.action_length = action.frame_range[1] - action.frame_range[0]


COMPARISON_ENUM_PROPERTY_ITEMS = [("less_than", "<", "Less than", 0),
                                  ("less_than_or_equal_to", "<=", "Less than or equal to", 1),
                                  ("equal_to", "=", "Equal to", 2),
                                  ("greater_than_or_equal_to", ">=", "Greater than or equal to", 3),
                                  ("greater_than", ">", "Greater than", 4)]

TIME_UNITS = [("frames", "Frames", "Frames", 0),
              ("seconds", "Seconds", "Seconds", 1)]


class NoteFilterProperty(PropertyGroup):
    filter_type: EnumProperty(items=NoteFilterImplementations.FILTER_ENUM_PROPERTY_ITEMS, name="Filter Type",
                              description="Filter Type", default="note_pitch_filter")
    comparison_operator: EnumProperty(items=COMPARISON_ENUM_PROPERTY_ITEMS, name="Comparison Operator",
                                      description="Comparison Operator", default="equal_to")
    note_pitch: EnumProperty(items=get_all_notes_for_pitch_filter, name="Pitch", description="Pitch")
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
        items=sorted(
            [(x, x, x, midi_data.ID_PROPERTIES_DICTIONARY[x][2]) for x in midi_data.ID_PROPERTIES_DICTIONARY.keys()],
            key=lambda x: x[0]),
        name="Type", description="Type of object to apply the action to", default="Object", update=on_id_type_updated)

    action: PointerProperty(type=bpy.types.Action, name="Action", description="The action to create action strips from",
                            poll=action_poll, update=on_action_updated)

    midi_frame_offset: \
        IntProperty(name="Frame Offset",
                    description="Frame offset when copying strips")

    nla_track_name: \
        StringProperty(name="Nla Track",
                       description="Name of the NLA Track that action strips will be placed on.\n " +
                                   "A track name will be automatically generated if this is blank")

    duplicate_object_on_overlap: \
        BoolProperty(name="Duplicate Object on Overlap",
                     description="Copy the action to a duplicated object if it overlaps another action",
                     default=False)

    blend_mode: \
        EnumProperty(items=midi_data.BLEND_MODES, name="Blending", description="Blending for overlapping strips",
                     default="REPLACE")

    sync_length_with_notes: \
        BoolProperty(name="Sync Length with Notes",
                     description="Scale the copied NLA strips so that their lengths match the lengths of the notes "
                                 "they are copied to",
                     default=False)

    copy_to_note_end: \
        BoolProperty(name="Copy to Note End",
                     description="Copy the action to the end of the note instead of the beginning",
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
                     default=False)

    action_length: \
        IntProperty(name="Action Length (Frames)",
                    min=1,
                    description="Length of the action, used to determine if the next action " +
                                "overlaps for object duplication. " +
                                "It has no effect on the actual length of the copied action.\n" +
                                "This option has no effect if \"Sync Length with Notes\" is selected.\n" +
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
    brush: PointerProperty(type=bpy.types.Brush, name="Brush", description="The brush to animate")
    camera: PointerProperty(type=bpy.types.Camera, name="Camera", description="The camera to animate")
    cachefile: PointerProperty(type=bpy.types.CacheFile, name="Cache File", description="The cache file to animate")
    collection: PointerProperty(type=bpy.types.Collection, name="Collection", description="The collection animate")
    curve: PointerProperty(type=bpy.types.Curve, name="Curve", description="The curve to animate")
    greasepencil: PointerProperty(type=bpy.types.GreasePencil, name="Grease Pencil",
                                  description="The grease pencil to animate")
    image: PointerProperty(type=bpy.types.Image, name="Image", description="The image to animate")
    key: PointerProperty(type=bpy.types.Key, name="Key", description="The key to animate")
    lattice: PointerProperty(type=bpy.types.Lattice, name="Lattice", description="The lattice to animate")
    light: PointerProperty(type=bpy.types.Light, name="Light", description="The light to animate")
    light_probe: PointerProperty(type=bpy.types.LightProbe, name="Light  Probe",
                                 description="The light_probe to animate")
    mask: PointerProperty(type=bpy.types.Mask, name="Mask", description="The mask to animate")
    material: PointerProperty(type=bpy.types.Material, name="Material", description="The material to animate")
    meta: PointerProperty(type=bpy.types.MetaBall, name="MetaBall", description="The meta to animate")
    mesh: PointerProperty(type=bpy.types.Mesh, name="Mesh", description="The mesh to animate")
    movieclip: PointerProperty(type=bpy.types.MovieClip, name="Movie Clip", description="The movie clip to animate")
    nodetree: PointerProperty(type=bpy.types.NodeTree, name="Node Tree", description="The node tree to animate")
    object: PointerProperty(type=bpy.types.Object, name="Object", description="The object to animate")
    paintcurve: PointerProperty(type=bpy.types.PaintCurve, name="Paintcurve", description="The paintcurve to animate")
    palette: PointerProperty(type=bpy.types.Palette, name="Palette", description="The palette to animate")
    scene: PointerProperty(type=bpy.types.Scene, name="Scene", description="The scene to animate")
    sound: PointerProperty(type=bpy.types.Sound, name="Sound", description="The sound to animate")
    speaker: PointerProperty(type=bpy.types.Speaker, name="Speaker", description="The speaker to animate")
    text: PointerProperty(type=bpy.types.Text, name="Text", description="The text to animate")
    texture: PointerProperty(type=bpy.types.Texture, name="Texture", description="The texture to animate")
    volume: PointerProperty(type=bpy.types.Volume, name="Volume", description="The volume to animate")
    world: PointerProperty(type=bpy.types.World, name="World", description="The world to animate")


class InstrumentNoteProperty(PropertyGroup):
    name: StringProperty(name="Name")
    note_id: IntProperty(name="Note")
    actions: CollectionProperty(type=NoteActionProperty, name="Actions")


TRANSPOSE_FILTER_ITEMS = \
    [("no_transpose", "Do not transpose", "Do not transpose", 0),
     ("transpose_if_possible_leave_all_inclusive", "Transpose if possible except all-inclusive",
      "Transpose filters if possible. Does not transpose filters that can't be transposed due to range constraints. "
      "Does not transpose filters than include every pitch", 1),
     ("transpose_if_possible", "Transpose if possible",
      "Transpose filters if possible. Does not transpose filters that can't be transposed due to range constraints", 2),
     ("transpose_all_leave_all_inclusive", "Transpose all except all-inclusive",
      "Transpose all filters except for filters than include every pitch", 3),
     ("transpose_all", "Transpose all", "Transpose all filters", 4)]


def instrument_note_filter_updated(self, context):
    # sometimes the selected note ends up blank, look for a note to select in that case
    if len(self.selected_note_id) == 0 and len(midi_data.midi_data.instrument_notes_list) > 0:
        self.selected_note_id = midi_data.midi_data.instrument_notes_list[0][0]


def midi_panel_instrument_note_filter_updated(self, context):
    # sometimes the selected note ends up blank, look for a note to select in that case
    if self.bulk_copy_property.copy_to_instrument:
        if len(self.copy_to_instrument_selected_note_id) == 0 and len(midi_data.midi_data.instrument_notes_list2) > 0:
            self.copy_to_instrument_selected_note_id = midi_data.midi_data.instrument_notes_list2[0][0]
    else:
        if len(self.copy_to_instrument_selected_note_id) == 0 and len(midi_data.midi_data.copy_panel_notes_list) > 0:
            self.copy_to_instrument_selected_note_id = midi_data.midi_data.copy_panel_notes_list[0][0]


def bulk_copy_start_note_filter_updated(bulk_copy_property, context):
    # sometimes the selected note ends up blank, look for a note to select in that case
    if len(bulk_copy_property.bulk_copy_starting_note) == 0 and len(
            midi_data.midi_data.bulk_copy_starting_notes_list) > 0:
        bulk_copy_property.bulk_copy_starting_note = midi_data.midi_data.bulk_copy_starting_notes_list[0][0]


class InstrumentProperty(PropertyGroup):
    name: StringProperty(name="Name")
    instrument_midi_frame_offset: IntProperty(name="Instrument Frame Offset",
                                              description="Frame offset when copying strips")
    notes: CollectionProperty(type=InstrumentNoteProperty, name="Notes")
    selected_note_id: EnumProperty(items=midi_data.get_instrument_notes,
                                   name="Note", description="Note")

    note_search_string: StringProperty(name="Search", description="Search notes", update=instrument_note_filter_updated)

    selected_midi_track: EnumProperty(items=get_tracks_list,
                                      name="Track",
                                      description="Selected Midi Track")
    copy_to_single_track: BoolProperty(name="Copy to single track",
                                       description="If selected, copy actions to a single nla track. "
                                                   "Otherwise create a track for each note. "
                                                   "This is overwritten for any actions that have an Nla Track",
                                       default=True)
    nla_track_name: StringProperty(name="Nla Track",
                                   description="Name of the nla track to copy actions to. "
                                               "A name will be generated of this field is blank. "
                                               "This field is not used if \"Copy to Single Track\" is not selected")
    # properties for drawing the panel
    properties_expanded: BoolProperty(name="Expanded", default=True)
    transpose_expanded: BoolProperty(name="Transpose:", default=False)
    notes_expanded: BoolProperty(name="Expanded", default=True)
    animate_expanded: BoolProperty(name="Expanded", default=True)
    transpose_filters: EnumProperty(items=TRANSPOSE_FILTER_ITEMS, name="Transpose Filters",
                                    description="Set how pitch filters will be transposed",
                                    default="transpose_all_leave_all_inclusive")


def get_midi_file_name(self):
    if "midi_file" in self:
        return self["midi_file"]
    return ""


middle_c_options = [("C3", "C3", "C3", 0), ("C4", "C4", "C4", 1), ("C5", "C5", "C5", 2)]


def update_middle_c(self, context):
    midi_data.midi_data.middle_c_id = self.middle_c_note


def update_notes_list(midi_property_group, context):
    copy_to_instrument = midi_property_group.copy_to_instrument_selected_instrument
    if copy_to_instrument is not None and copy_to_instrument != midi_data.NO_INSTRUMENT_SELECTED and \
            not midi_property_group.copy_to_instrument_note_search_string:
        # update the selected note in the copy to instrument panel to match
        midi_property_group.copy_to_instrument_selected_note_id = str(PitchUtils.note_pitch_from_id(
            midi_property_group.notes_list))


def object_is_curve(bulk_copy_property_group, bpy_object):
    return bpy_object.type == "CURVE"


scale_filter_options = [("No filter", "No filter", "Do not filter by scale", 0),
                        ("In scale", "In scale", "Only include nodes in the selected scale", 1),
                        ("Not in scale", "Not in scale", "Only include notes that are not in the selected scale", 2)]
scale_options = [("A", "A", "A", 9), ("A#", "A#", "A#", 10), ("B", "B", "B", 11), ("C", "C", "C", 0),
                 ("C#", "C#", "C#", 1), ("D", "D", "D", 2), ("D#", "D#", "D#", 3), ("E", "E", "E", 4),
                 ("F", "F", "F", 5), ("F#", "F#", "F#", 6), ("G", "G", "G", 7), ("G#", "G#", "G#", 8), ]


class BulkCopyPropertyGroup(PropertyGroup):
    copy_along_path: BoolProperty(name="Copy along path",
                                  description="Animate selected objects, ordered by a path.\n"
                                              "Each object is animated to a different note, ascending by pitch along "
                                              "the path")
    copy_along_path_options_expanded: BoolProperty(name="Expanded", default=True)
    copy_to_instrument: BoolProperty(name="Copy to Instrument", default=False,
                                     description="Copies actions to an instrument if selected, otherwise copies "
                                                 "actions directly to NLA strips")
    bulk_copy_curve: PointerProperty(type=bpy.types.Object, name="Path", poll=object_is_curve,
                                     description="The path of selected objects to animate")
    bulk_copy_starting_note: EnumProperty(items=midi_data.get_bulk_copy_starting_note,
                                          name="Starting Note", description="The note to use for the first object")
    bulk_copy_starting_note_search_string: StringProperty(name="Search", description="Search notes",
                                                          update=bulk_copy_start_note_filter_updated)
    scale_filter_type: EnumProperty(items=scale_filter_options, name="Filter by Scale", description="Filter by Scale")
    scale_filter_scale: EnumProperty(items=scale_options, name="Scale", description="Major Scale")
    only_notes_in_selected_track: BoolProperty(name="Only Notes in Selected Track",
                                               description="Only copy to notes in the selected Track "
                                                           "in the NLA Midi Panel",
                                               default=False)


def get_midi_file_beats_per_minute(self):
    if "file_beats_per_minute" in self:
        return self["file_beats_per_minute"]
    return 0


def get_midi_file_ticks_per_beat(self):
    if "file_ticks_per_beat" in self:
        return self["file_ticks_per_beat"]
    return 0


def on_tempo_property_update(tempo_property, context):
    midi_data.midi_data.update_tempo(context)


class TempoPropertyGroup(PropertyGroup):
    use_file_tempo: BoolProperty(name="File Tempo", default=True,
                                 description="Use the tempo defined by the midi file", update=on_tempo_property_update)
    beats_per_minute: FloatProperty(name="Bpm", default=120, description="Beats per minute",
                                    update=on_tempo_property_update, min=0.01)
    # defining get= (and not set=) disables editing in the UI
    file_beats_per_minute: FloatProperty(name="Bpm", default=120, description="Beats per minute",
                                         get=get_midi_file_beats_per_minute, update=on_tempo_property_update)
    use_file_ticks_per_beat: BoolProperty(name="File Ticks per Beat", default=True,
                                          description="Use the ticks per beat defined by the midi file. "
                                                      "(Selecting this and changing only the beats per minute should be"
                                                      " sufficient for most tempo changes.)",
                                          update=on_tempo_property_update)
    ticks_per_beat: IntProperty(name="Ticks per beat", default=96, description="Ticks per beat", min=1,
                                update=on_tempo_property_update)
    # defining get= (and not set=) disables editing in the UI
    file_ticks_per_beat: IntProperty(name="Ticks per beat", default=96, description="Ticks per beat",
                                     get=get_midi_file_ticks_per_beat, update=on_tempo_property_update)


class MidiPropertyGroup(PropertyGroup):
    # defining get= (and not set=) disables editing in the UI
    midi_file: StringProperty(name="Midi File", description="Select Midi File", get=get_midi_file_name)
    notes_list: EnumProperty(items=get_notes_list,
                             name="Note",
                             description="Note",
                             update=update_notes_list)
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

    copy_to_instrument_selected_instrument: EnumProperty(items=midi_data.get_instruments, name="Instrument",
                                                         description="Instrument to copy the action to")
    copy_to_instrument_selected_note_id: EnumProperty(items=midi_data.get_selected_instrument_notes,
                                                      name="Note", description="Note to copy the action to")
    copy_to_instrument_note_search_string: StringProperty(name="Search", description="Search notes",
                                                          update=midi_panel_instrument_note_filter_updated)
    bulk_copy_property: PointerProperty(type=BulkCopyPropertyGroup)

    middle_c_note: EnumProperty(items=middle_c_options,
                                name="Middle C", description="The note corresponding to middle C (midi note 60)",
                                default="C4", update=update_middle_c)
    tempo_settings: PointerProperty(type=TempoPropertyGroup)
