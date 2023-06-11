if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PitchUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PropertyUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(CompatibilityModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from . import midi_data
    from . import NoteFilterImplementations
    from . import PitchUtils
    from . import PropertyUtils
    from . import CompatibilityModule
    from .i18n import i18n

import bpy
from bpy.app import version as blender_version
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, PointerProperty, CollectionProperty, \
    FloatProperty
from bpy.types import PropertyGroup
from .midi_data import MidiDataType, LoadedMidiData


def get_all_notes_for_pitch_filter(note_filter_property, context):
    return midi_data.get_midi_data(note_filter_property.data_type).get_all_notes_for_pitch_filter(context)


def get_tracks_list(midi_property_group, context):
    return midi_data.get_midi_data(midi_property_group.data_type).get_tracks_list(midi_property_group, context)


def get_notes_list(midi_property_group, context):
    return midi_data.get_midi_data(midi_property_group.data_type).get_notes_list(context)


def action_poll(note_action_property, action):
    id_root = midi_data.ID_PROPERTIES_DICTIONARY[note_action_property.id_type][1]
    return action.id_root == id_root or (
            action.id_root == "NODETREE" and id_root in midi_data.node_tree_types)


def get_instruments(midi_data_property, context):
    return midi_data.get_midi_data(MidiDataType.NLA).get_instruments(midi_data_property, context)


def get_instrument_notes(instrument_property, context):
    return midi_data.get_midi_data(MidiDataType.NLA).get_instrument_notes(instrument_property,
                                                                          LoadedMidiData.store_notes_list_one)


def get_bulk_copy_starting_note(bulk_copy_property, context):
    # enum property for the starting note for bulk copy
    return midi_data.get_midi_data(MidiDataType.NLA).get_all_notes_list()


def get_notes_for_copy_panel(midi_data_property, context):
    """
    :return: the notes for the selected instrument in the Copy panel, or all notes if copy to instrument is not selected
    """
    if midi_data_property.bulk_copy_property.copy_to_instrument:
        loaded_midi_data = midi_data.get_midi_data(MidiDataType.NLA)
        return loaded_midi_data.get_instrument_notes(
            loaded_midi_data.selected_instrument_for_copy_to_id(context),
            LoadedMidiData.store_notes_list_two)
    else:
        return midi_data.get_midi_data(MidiDataType.NLA).get_all_notes_list()


def on_id_type_updated(note_action_property, context):
    # clear the action since it no longer applies to the selected id type
    note_action_property.action = None
    if note_action_property.copy_to_selected_objects and \
            not midi_data.can_resolve_data_from_selected_objects(note_action_property.id_type):
        # copy to selected objects only works if selected data can be resolved from the id_type
        note_action_property.copy_to_selected_objects = False
    # duplicate objects only works if id_type corresponds to an object type
    if note_action_property.on_overlap == '' or \
            (note_action_property.on_overlap == "DUPLICATE_OBJECTS" and not midi_data.id_type_is_object(
                note_action_property.id_type)):
        note_action_property.on_overlap = "BLEND"


def on_action_updated(note_action_property, context):
    action = note_action_property.action
    # update the action length property to match the actual length of the action
    if action is not None:
        note_action_property.action_length = int(action.frame_range[1]) - int(action.frame_range[0])


COMPARISON_ENUM_PROPERTY_ITEMS = [("less_than", "<", i18n.get_key(i18n.LESS_THAN), 0),
                                  ("less_than_or_equal_to", "<=", i18n.get_key(i18n.LESS_THAN_OR_EQUAL_TO), 1),
                                  ("equal_to", "=", i18n.get_key(i18n.EQUAL_TO), 2),
                                  ("greater_than_or_equal_to", ">=", i18n.get_key(i18n.GREATER_THAN_OR_EQUAL_TO), 3),
                                  ("greater_than", ">", i18n.get_key(i18n.GREATER_THAN), 4)]

TIME_UNITS = [("frames", i18n.get_key(i18n.FRAMES), i18n.get_key(i18n.FRAMES), 0),
              ("seconds", i18n.get_key(i18n.SECONDS), i18n.get_key(i18n.SECONDS), 1)]


class NoteFilterPropertyBase:
    filter_type: EnumProperty(items=NoteFilterImplementations.FILTER_ENUM_PROPERTY_ITEMS,
                              name=i18n.get_key(i18n.FILTER_TYPE), description=i18n.get_key(i18n.FILTER_TYPE),
                              default="note_pitch_filter")
    comparison_operator: EnumProperty(items=COMPARISON_ENUM_PROPERTY_ITEMS, name=i18n.get_key(i18n.COMPARISON_OPERATOR),
                                      description=i18n.get_key(i18n.COMPARISON_OPERATOR), default="equal_to")
    note_pitch: PropertyUtils.note_property(i18n.get_key(i18n.PITCH), i18n.get_key(i18n.PITCH),
                                            get_all_notes_for_pitch_filter,
                                            "note_pitch", "note_pitch_search_string")
    note_pitch_search_string: PropertyUtils.note_search_property("note_pitch", "note_pitch_search_string",
                                                                 get_all_notes_for_pitch_filter)
    non_negative_int: IntProperty(name=i18n.get_key(i18n.NON_NEGATIVE_INT),
                                  description=i18n.get_key(i18n.NON_NEGATIVE_INTEGER), min=0)
    positive_int: IntProperty(name=i18n.get_key(i18n.POSITIVE_INT), description=i18n.get_key(i18n.POSITIVE_INTEGER),
                              min=1, default=1)
    positive_int_2: IntProperty(name=i18n.get_key(i18n.POSITIVE_INT), description=i18n.get_key(i18n.POSITIVE_INTEGER),
                                min=1, default=1)
    int_0_to_127: IntProperty(name=i18n.get_key(i18n.INTEGER),
                              description=i18n.get_key(i18n.INTEGER_0_TO_127_INCLUSIVE), min=0, max=127)
    non_negative_number: FloatProperty(name=i18n.get_key(i18n.NON_NEGATIVE_NUMBER),
                                       description=i18n.get_key(i18n.NON_NEGATIVE_NUMBER), min=0.0)
    time_unit: EnumProperty(items=TIME_UNITS, name=i18n.get_key(i18n.TIME_UNIT),
                            description=i18n.get_key(i18n.TIME_UNIT), default="frames")


class NoteFilterProperty(PropertyGroup, NoteFilterPropertyBase):
    data_type = MidiDataType.NLA


class NoteFilterGroup(PropertyGroup):
    note_filters: CollectionProperty(type=NoteFilterProperty, name=i18n.get_key(i18n.NOTE_FILTERS))
    expanded: BoolProperty(name="Expanded", default=True)


class NoteActionPropertyBase:
    midi_frame_offset: \
        IntProperty(name=i18n.get_key(i18n.FRAME_OFFSET),
                    description=i18n.get_key(i18n.FRAME_OFFSET_WHEN_COPYING_STRIPS))
    add_filters: \
        BoolProperty(name=i18n.get_key(i18n.ADD_FILTERS),
                     description=i18n.get_key(i18n.ADD_FILTERS_DESCRIPTION),
                     default=False)
    filters_expanded: BoolProperty(name="Expanded", default=True)
    scale_factor: \
        FloatProperty(name=i18n.get_key(i18n.SCALE_FACTOR),
                      description=i18n.get_key(i18n.SCALE_FACTOR_DESCRIPTION),
                      min=0.0000001, max=1000000, soft_min=0.0000001, soft_max=1000000, default=1)
    copy_to_note_end: \
        BoolProperty(name=i18n.get_key(i18n.COPY_TO_NOTE_END),
                     description=i18n.get_key(i18n.COPY_TO_NOTE_END_DESCRIPTION),
                     default=False)


OVERLAP_OPTIONS = [("SKIP", i18n.get_key(i18n.SKIP), i18n.get_key(i18n.OVERLAP_SKIP_DESCRIPTION), 0),
                   ("BLEND", i18n.get_key(i18n.BLEND),
                    i18n.get_key(i18n.OVERLAP_BLEND_DESCRIPTION), 1),
                   ("DUPLICATE_OBJECT", i18n.get_key(i18n.DUPLICATE_OBJECT),
                    i18n.get_key(i18n.DUPLICATE_OBJECT_DESCRIPTION), 2)]

OVERLAP_OPTIONS_WITHOUT_DUPLICATE = [x for x in OVERLAP_OPTIONS if x[0] != "DUPLICATE_OBJECT"]


def get_overlap_options(note_action_property, context):
    return OVERLAP_OPTIONS if midi_data.id_type_is_object(
        note_action_property.id_type) else OVERLAP_OPTIONS_WITHOUT_DUPLICATE


def get_blend_modes(note_action_property, context):
    return midi_data.BLEND_MODES if CompatibilityModule.compatibility_updates_complete \
        else midi_data.BLEND_MODES_DEPRECATED




SYNC_LENGTH_ACTION_TIMING_MODES = \
    [("scale_action_length", i18n.get_key(i18n.SCALE_ACTION_LENGTH), i18n.get_key(i18n.SCALE_ACTION_LENGTH), 0),
     ("repeat_action", i18n.get_key(i18n.REPEAT), i18n.get_key(i18n.REPEAT_ACTION_LENGTH_DESCRIPTION), 1)]


class NoteActionProperty(PropertyGroup, NoteActionPropertyBase):
    data_type = MidiDataType.NLA
    id_type: EnumProperty(
        items=sorted(
            [(x, x, x, midi_data.ID_PROPERTIES_DICTIONARY[x][2], midi_data.ID_PROPERTIES_DICTIONARY[x][3]) for x in
             midi_data.ID_PROPERTIES_DICTIONARY.keys()],
            key=lambda x: x[0]),
        name=i18n.get_key(i18n.TYPE), description=i18n.get_key(i18n.TYPE_DESCRIPTION), default="Object",
        update=on_id_type_updated)

    action: PointerProperty(type=bpy.types.Action, name=i18n.get_key(i18n.ACTION),
                            description=i18n.get_key(i18n.ACTION_DESCRIPTION),
                            poll=action_poll, update=on_action_updated)

    nla_track_name: \
        StringProperty(name=i18n.get_key(i18n.NLA_TRACK),
                       description=i18n.get_key(i18n.NLA_TRACK_DESCRIPTION))

    # deprecated, on_overlap used instead
    duplicate_object_on_overlap: \
        BoolProperty(name=i18n.get_key(i18n.DUPLICATE_OBJECT_ON_OVERLAP),
                     description=i18n.get_key(i18n.DUPLICATE_OBJECT_ON_OVERLAP_DESCRIPTION),
                     default=False)

    on_overlap: EnumProperty(items=get_overlap_options, name=i18n.get_key(i18n.OVERLAP),
                             description=i18n.get_key(i18n.HOW_TO_HANDLE_OVERLAPPING_ACTIONS),
                             default=PropertyUtils.dynamic_enum_default(1))  # default to Blend

    blend_mode: \
        EnumProperty(items=get_blend_modes, name=i18n.get_key(i18n.BLENDING),
                     description=i18n.get_key(i18n.BLENDING_FOR_OVERLAPPING_STRIPS),
                     default=PropertyUtils.dynamic_enum_default(1))  # default to Replace

    sync_length_with_notes: \
        BoolProperty(name=i18n.get_key(i18n.SYNC_LENGTH_WITH_NOTES),
                     description=i18n.get_key(i18n.SYNC_LENGTH_WITH_NOTES_DESCRIPTION),
                     default=False)
    sync_length_action_timing_mode: \
        EnumProperty(items=SYNC_LENGTH_ACTION_TIMING_MODES,
                     name=i18n.get_key(i18n.ACTION_TIMING),
                     description=i18n.get_key(i18n.ACTION_TIMING),
                     default="scale_action_length")

    note_filter_groups: CollectionProperty(type=NoteFilterGroup, name=i18n.get_key(i18n.NOTE_FILTER_GROUPS))

    copy_to_selected_objects: \
        BoolProperty(name=i18n.get_key(i18n.COPY_ACTION_TO_SELECTED_OBJECTS),
                     description=i18n.get_key(i18n.COPY_TO_SELECTED_OBJECTS_DESCRIPTION),
                     default=False)

    action_length: \
        IntProperty(name=i18n.get_key(i18n.ACTION_LENGTH_FRAMES),
                    min=1,
                    description=i18n.get_key(i18n.ACTION_LENGTH_FRAMES_DESCRIPTION))

    # used for display in the instruments panel
    expanded: BoolProperty(name="Expanded", default=True)

    armature: PointerProperty(type=bpy.types.Armature, name=i18n.get_key(i18n.ARMATURE),
                              description=i18n.get_key(i18n.ARMATURE_TO_ANIMATE))
    brush: PointerProperty(type=bpy.types.Brush, name=i18n.get_key(i18n.BRUSH),
                           description=i18n.get_key(i18n.BRUSH_TO_ANIMATE))
    camera: PointerProperty(type=bpy.types.Camera, name=i18n.get_key(i18n.CAMERA),
                            description=i18n.get_key(i18n.CAMERA_TO_ANIMATE))
    cachefile: PointerProperty(type=bpy.types.CacheFile, name=i18n.get_key(i18n.CACHE_FILE),
                               description=i18n.get_key(i18n.CACHE_FILE_TO_ANIMATE))
    collection: PointerProperty(type=bpy.types.Collection, name=i18n.get_key(i18n.COLLECTION),
                                description=i18n.get_key(i18n.COLLECTION_TO_ANIMATE))
    curve: PointerProperty(type=bpy.types.Curve, name=i18n.get_key(i18n.CURVE),
                           description=i18n.get_key(i18n.CURVE_TO_ANIMATE))
    greasepencil: PointerProperty(type=bpy.types.GreasePencil, name=i18n.get_key(i18n.GREASE_PENCIL),
                                  description=i18n.get_key(i18n.GREASE_PENCIL_TO_ANIMATE))
    image: PointerProperty(type=bpy.types.Image, name=i18n.get_key(i18n.IMAGE),
                           description=i18n.get_key(i18n.IMAGE_TO_ANIMATE))
    key: PointerProperty(type=bpy.types.Key, name=i18n.get_key(i18n.KEY), description=i18n.get_key(i18n.KEY_TO_ANIMATE))
    lattice: PointerProperty(type=bpy.types.Lattice, name=i18n.get_key(i18n.LATTICE),
                             description=i18n.get_key(i18n.LATTICE_TO_ANIMATE))
    light: PointerProperty(type=bpy.types.Light, name=i18n.get_key(i18n.LIGHT),
                           description=i18n.get_key(i18n.LIGHT_TO_ANIMATE))
    light_probe: PointerProperty(type=bpy.types.LightProbe, name=i18n.get_key(i18n.LIGHT_PROBE),
                                 description=i18n.get_key(i18n.LIGHT_PROBE_TO_ANIMATE))
    mask: PointerProperty(type=bpy.types.Mask, name=i18n.get_key(i18n.MASK),
                          description=i18n.get_key(i18n.MASK_TO_ANIMATE))
    material: PointerProperty(type=bpy.types.Material, name=i18n.get_key(i18n.MATERIAL),
                              description=i18n.get_key(i18n.MATERIAL_TO_ANIMATE))
    meta: PointerProperty(type=bpy.types.MetaBall, name=i18n.get_key(i18n.METABALL),
                          description=i18n.get_key(i18n.METABALL_TO_ANIMATE))
    mesh: PointerProperty(type=bpy.types.Mesh, name=i18n.get_key(i18n.MESH),
                          description=i18n.get_key(i18n.MESH_TO_ANIMATE))
    movieclip: PointerProperty(type=bpy.types.MovieClip, name=i18n.get_key(i18n.MOVIE_CLIP),
                               description=i18n.get_key(i18n.MOVIE_CLIP_TO_ANIMATE))
    nodetree: PointerProperty(type=bpy.types.NodeTree, name=i18n.get_key(i18n.NODE_TREE),
                              description=i18n.get_key(i18n.THE_NODE_TREE_TO_ANIMATE))
    object: PointerProperty(type=bpy.types.Object, name=i18n.get_key(i18n.OBJECT),
                            description=i18n.get_key(i18n.OBJECT_TO_ANIMATE))
    paintcurve: PointerProperty(type=bpy.types.PaintCurve, name=i18n.get_key(i18n.PAINTCURVE),
                                description=i18n.get_key(i18n.PAINTCURVE_TO_ANIMATE))
    palette: PointerProperty(type=bpy.types.Palette, name=i18n.get_key(i18n.PALETTE),
                             description=i18n.get_key(i18n.PALETTE_TO_ANIMATE))
    particle_settings: PointerProperty(type=bpy.types.ParticleSettings, name=i18n.get_key(i18n.PARTICLE_SETTINGS),
                                       description=i18n.get_key(i18n.PARTICLE_SETTINGS_TO_ANIMATE))
    scene: PointerProperty(type=bpy.types.Scene, name=i18n.get_key(i18n.SCENE),
                           description=i18n.get_key(i18n.SCENE_TO_ANIMATE))
    sound: PointerProperty(type=bpy.types.Sound, name=i18n.get_key(i18n.SOUND),
                           description=i18n.get_key(i18n.SOUND_TO_ANIMATE))
    speaker: PointerProperty(type=bpy.types.Speaker, name=i18n.get_key(i18n.SPEAKER),
                             description=i18n.get_key(i18n.SPEAKER_TO_ANIMATE))
    text: PointerProperty(type=bpy.types.Text, name=i18n.get_key(i18n.TEXT),
                          description=i18n.get_key(i18n.TEXT_TO_ANIMATE))
    texture: PointerProperty(type=bpy.types.Texture, name=i18n.get_key(i18n.TEXTURE),
                             description=i18n.get_key(i18n.TEXTURE_TO_ANIMATE))
    if blender_version >= (2, 83, 0):
        volume: PointerProperty(type=bpy.types.Volume, name=i18n.get_key(i18n.VOLUME),
                                description=i18n.get_key(i18n.VOLUME_TO_ANIMATE))
    world: PointerProperty(type=bpy.types.World, name=i18n.get_key(i18n.WORLD),
                           description=i18n.get_key(i18n.WORLD_TO_ANIMATE))


class InstrumentNoteProperty(PropertyGroup):
    name: StringProperty(name=i18n.get_key(i18n.NAME))
    note_id: IntProperty(name=i18n.get_key(i18n.NOTE))
    actions: CollectionProperty(type=NoteActionProperty, name=i18n.get_key(i18n.ACTIONS))


TRANSPOSE_FILTER_ITEMS = \
    [("no_transpose", i18n.get_key(i18n.DO_NOT_TRANSPOSE), i18n.get_key(i18n.DO_NOT_TRANSPOSE), 0),
     ("transpose_if_possible_leave_all_inclusive", i18n.get_key(i18n.TRANSPOSE_IF_POSSIBLE_EXCEPT_ALL_INCLUSIVE),
      i18n.get_key(i18n.TRANSPOSE_IF_POSSIBLE_EXCEPT_ALL_DESCRIPTION), 1),
     ("transpose_if_possible", i18n.get_key(i18n.TRANSPOSE_IF_POSSIBLE),
      i18n.get_key(i18n.TRANSPOSE_IF_POSSIBLE_DESCRIPTION), 2),
     ("transpose_all_leave_all_inclusive", i18n.get_key(i18n.TRANSPOSE_EXCEPT_ALL_INCLUSIVE),
      i18n.get_key(i18n.TRANSPOSE_EXCEPT_ALL_INCLUSIVE_DESCRIPTION), 3),
     ("transpose_all", i18n.get_key(i18n.TRANSPOSE_ALL), i18n.get_key(i18n.TRANSPOSE_ALL_FILTERS), 4)]


class InstrumentProperty(PropertyGroup):
    data_type = MidiDataType.NLA
    name: StringProperty(name=i18n.get_key(i18n.NAME))
    instrument_midi_frame_offset: IntProperty(name=i18n.get_key(i18n.INSTRUMENT_FRAME_OFFSET),
                                              description=i18n.get_key(i18n.FRAME_OFFSET_WHEN_COPYING_STRIPS))
    notes: CollectionProperty(type=InstrumentNoteProperty, name=i18n.get_key(i18n.NOTES))
    selected_note_id: PropertyUtils.note_property(i18n.get_key(i18n.NOTE), i18n.get_key(i18n.NOTE),
                                                  get_instrument_notes,
                                                  "selected_note_id", "note_search_string")

    note_search_string: PropertyUtils.note_search_property("selected_note_id", "note_search_string",
                                                           get_instrument_notes)

    selected_midi_track: EnumProperty(items=get_tracks_list,
                                      name=i18n.get_key(i18n.TRACK),
                                      description=i18n.get_key(i18n.SELECTED_MIDI_TRACK))
    copy_to_single_track: BoolProperty(name=i18n.get_key(i18n.COPY_TO_SINGLE_TRACK),
                                       description=i18n.get_key(i18n.COPY_TO_SINGLE_TRACK_DESCRIPTION),
                                       default=True)
    nla_track_name: StringProperty(name=i18n.get_key(i18n.NLA_TRACK),
                                   description=i18n.get_key(i18n.NLA_TRACK_INSTRUMENT_DESCRIPTION))
    # properties for drawing the panel
    properties_expanded: BoolProperty(name="Expanded", default=True)
    transpose_expanded: BoolProperty(name="Transpose:", default=False)
    notes_expanded: BoolProperty(name="Expanded", default=True)
    animate_expanded: BoolProperty(name="Expanded", default=True)
    transpose_filters: EnumProperty(items=TRANSPOSE_FILTER_ITEMS, name=i18n.get_key(i18n.TRANSPOSE_FILTERS),
                                    description=i18n.get_key(i18n.TRANSPOSE_FILTERS_DESCRIPTION),
                                    default="transpose_all_leave_all_inclusive")


def get_midi_file_name(self):
    if "midi_file" in self:
        return self["midi_file"]
    return ""


middle_c_options = [("C3", "C3", "C3", 0), ("C4", "C4", "C4", 1), ("C5", "C5", "C5", 2)]


def on_track_updated(midi_property_group, context):
    # select the first note in the track
    loaded_midi_data = midi_data.get_midi_data(midi_property_group.data_type)
    notes_list = loaded_midi_data.get_notes_list(context)
    if len(notes_list) > 0:
        midi_property_group.notes_list = loaded_midi_data.get_notes_list(context)[0][0]


def on_middle_c_updated(midi_property_group, context):
    midi_data.get_midi_data(midi_property_group.data_type).middle_c_id = midi_property_group.middle_c_note


def on_track_name_updated(track_property_group, context):
    midi_data.get_midi_data(track_property_group.midi_data_type).update_track_names(context)


def update_notes_list(midi_property_group, context):
    if get_notes_for_copy_panel(midi_property_group, context):
        # update the note for copying to an instrument in the quick copy tools panel to match
        midi_property_group.copy_to_instrument_selected_note_id = str(PitchUtils.note_pitch_from_id(
            midi_property_group.notes_list))
    PropertyUtils.note_updated_function("notes_list", "note_search_string", get_notes_list)(midi_property_group,
                                                                                            context)


def object_is_curve(bulk_copy_property_group, bpy_object):
    return bpy_object.type == "CURVE"


scale_filter_options = [("no_filter", i18n.get_key(i18n.NO_FILTER), i18n.get_key(i18n.DO_NOT_FILTER_BY_SCALE), 0),
                        ("in_scale", i18n.get_key(i18n.IN_SCALE), i18n.get_key(i18n.IN_SCALE_DESCRIPTION), 1),
                        ("not_in_scale", i18n.get_key(i18n.NOT_IN_SCALE), i18n.get_key(i18n.NOT_IN_SCALE_DESCRIPTION),
                         2)]
scale_options = [("A", "A", "A", 9), ("A#", "A#", "A#", 10), ("B", "B", "B", 11), ("C", "C", "C", 0),
                 ("C#", "C#", "C#", 1), ("D", "D", "D", 2), ("D#", "D#", "D#", 3), ("E", "E", "E", 4),
                 ("F", "F", "F", 5), ("F#", "F#", "F#", 6), ("G", "G", "G", 7), ("G#", "G#", "G#", 8), ]
copy_tools = [("copy_to_instrument", i18n.get_key(i18n.COPY_TO_INSTRUMENT), i18n.get_key(i18n.COPY_TO_INSTRUMENT), 0),
              ("copy_along_path", i18n.get_key(i18n.COPY_ALONG_PATH),
               i18n.get_key(i18n.COPY_ALONG_PATH_DESCRIPTION), 1),
              ("copy_by_object_name", i18n.get_key(i18n.COPY_BY_OBJECT_NAME),
               i18n.get_key(i18n.COPY_BY_OBJECT_NAME_DESCRIPTION), 2)]
copy_by_name_type = [("copy_by_note", i18n.get_key(i18n.COPY_BY_NOTE_NAME),
                      i18n.get_key(i18n.COPY_BY_NOTE_NAME_DESCRIPTION), 0),
                     ("copy_by_track_and_note", i18n.get_key(i18n.COPY_BY_TRACK_AND_NOTE_NAME),
                      i18n.get_key(i18n.COPY_BY_TRACK_AND_NOTE_NAME_DESCRIPTION), 1)]


class BulkCopyPropertyGroup(PropertyGroup):
    quick_copy_tool: EnumProperty(name=i18n.get_key(i18n.QUICK_COPY_TOOL),
                                  description=i18n.get_key(i18n.QUICK_COPY_TOOL), items=copy_tools,
                                  default="copy_by_object_name")
    copy_to_instrument: BoolProperty(name=i18n.get_key(i18n.COPY_TO_INSTRUMENT), default=False,
                                     description=i18n.get_key(i18n.COPY_TO_INSTRUMENT_DESCRIPTION))
    selected_objects_only: BoolProperty(name=i18n.get_key(i18n.COPY_TO_SELECTED_OBJECTS_ONLY), default=True,
                                        description=i18n.get_key(i18n.COPY_TO_SELECTED_OBJECTS_ONLY_DESCRIPTION))
    bulk_copy_curve: PointerProperty(type=bpy.types.Object, name=i18n.get_key(i18n.PATH), poll=object_is_curve,
                                     description=i18n.get_key(i18n.COPY_ALONG_PATH_CURVE_DESCRIPTION))
    bulk_copy_starting_note: \
        PropertyUtils.note_property(i18n.get_key(i18n.STARTING_NOTE),
                                    i18n.get_key(i18n.COPY_ALONG_PATH_STARTING_NOTE_DESCRIPTION),
                                    get_bulk_copy_starting_note,
                                    "bulk_copy_starting_note", "bulk_copy_starting_note_search_string")
    bulk_copy_starting_note_search_string: \
        PropertyUtils.note_search_property("bulk_copy_starting_note", "bulk_copy_starting_note_search_string",
                                           get_bulk_copy_starting_note)
    scale_filter_type: EnumProperty(items=scale_filter_options, name=i18n.get_key(i18n.FILTER_BY_SCALE),
                                    description=i18n.get_key(i18n.FILTER_BY_SCALE))
    scale_filter_scale: EnumProperty(items=scale_options, name=i18n.get_key(i18n.SCALE),
                                     description=i18n.get_key(i18n.MAJOR_SCALE))
    only_notes_in_selected_track: BoolProperty(name=i18n.get_key(i18n.ONLY_NOTES_IN_SELECTED_TRACK),
                                               description=i18n.get_key(i18n.ONLY_NOTES_IN_SELECTED_TRACK_DESCRIPTION),
                                               default=False)
    copy_by_name_type: EnumProperty(name=i18n.get_key(i18n.COPY_BY), description=i18n.get_key(i18n.COPY_BY_NAME),
                                    items=copy_by_name_type, default="copy_by_note")


def get_midi_file_beats_per_minute(tempo_property):
    if "file_beats_per_minute" in tempo_property:
        return tempo_property["file_beats_per_minute"]
    return 0


def get_midi_file_ticks_per_beat(tempo_property):
    if "file_ticks_per_beat" in tempo_property:
        return tempo_property["file_ticks_per_beat"]
    return 0


def on_tempo_property_update(tempo_property, context):
    midi_data.get_midi_data(tempo_property.data_type).update_tempo(context)


class TempoPropertyBase:
    use_file_tempo: BoolProperty(name=i18n.get_key(i18n.FILE_TEMPO), default=True,
                                 description=i18n.get_key(i18n.FILE_TEMPO_DESCRIPTION), update=on_tempo_property_update)
    beats_per_minute: FloatProperty(name=i18n.get_key(i18n.BPM), default=120,
                                    description=i18n.get_key(i18n.BEATS_PER_MINUTE),
                                    update=on_tempo_property_update, min=0.01)
    # defining get= (and not set=) disables editing in the UI
    file_beats_per_minute: FloatProperty(name=i18n.get_key(i18n.BPM), default=120,
                                         description=i18n.get_key(i18n.BEATS_PER_MINUTE),
                                         get=get_midi_file_beats_per_minute, update=on_tempo_property_update)
    use_file_ticks_per_beat: BoolProperty(name=i18n.get_key(i18n.FILE_TICKS_PER_BEAT), default=True,
                                          description=i18n.get_key(i18n.FILE_TICKS_PER_BEAT_DESCRIPTION),
                                          update=on_tempo_property_update)
    ticks_per_beat: IntProperty(name=i18n.get_key(i18n.TICKS_PER_BEAT), default=96,
                                description=i18n.get_key(i18n.TICKS_PER_BEAT), min=1, update=on_tempo_property_update)
    # defining get= (and not set=) disables editing in the UI
    file_ticks_per_beat: IntProperty(name=i18n.get_key(i18n.TICKS_PER_BEAT), default=96,
                                     description=i18n.get_key(i18n.TICKS_PER_BEAT),
                                     get=get_midi_file_ticks_per_beat, update=on_tempo_property_update)


class TempoPropertyGroup(PropertyGroup, TempoPropertyBase):
    data_type = MidiDataType.NLA


class MidiTrackProperty(PropertyGroup):
    midi_data_type: IntProperty(name="MidiDataType")
    midi_track_name: StringProperty(name=i18n.get_key(i18n.MIDI_TRACK),
                                    description=i18n.get_key(i18n.MIDI_TRACK_DESCRIPTION))
    displayed_track_name: StringProperty(name=i18n.get_key(i18n.DISPLAYED_NAME),
                                         description=i18n.get_key(i18n.DISPLAYED_TRACK_NAME_DESCRIPTION),
                                         update=on_track_name_updated)


class MidiPropertyBase:
    # defining get= (and not set=) disables editing in the UI
    midi_file: StringProperty(name=i18n.get_key(i18n.MIDI_FILE), description=i18n.get_key(i18n.SELECTED_MIDI_FILE),
                              get=get_midi_file_name)
    # the selected note
    notes_list: PropertyUtils.note_property(i18n.get_key(i18n.NOTE), i18n.get_key(i18n.NOTE), get_notes_list,
                                            "notes_list", "note_search_string")
    note_search_string: PropertyUtils.note_search_property("notes_list", "note_search_string",
                                                           get_notes_list)
    track_list: EnumProperty(items=get_tracks_list,
                             name=i18n.get_key(i18n.TRACK),
                             description=i18n.get_key(i18n.SELECTED_MIDI_TRACK),
                             update=on_track_updated)
    note_action_property: PointerProperty(type=NoteActionProperty)
    midi_frame_start: \
        IntProperty(name=i18n.get_key(i18n.FIRST_FRAME),
                    description=i18n.get_key(i18n.FIRST_FRAME_DESCRIPTION),
                    default=1)
    middle_c_note: EnumProperty(items=middle_c_options,
                                name=i18n.get_key(i18n.MIDDLE_C), description=i18n.get_key(i18n.MIDDLE_C_DESCRIPTION),
                                default="C4", update=on_middle_c_updated)
    tempo_settings: PointerProperty(type=TempoPropertyGroup)
    midi_track_properties: CollectionProperty(type=MidiTrackProperty, name=i18n.get_key(i18n.DISPLAYED_TRACK_NAMES))
    midi_track_property_index: IntProperty()


# region Other tools properties
# note: would be nice to have these in another file but that seems to be causing issues with reloading the script
INTERPOLATIONS = [("CONSTANT", i18n.get_key(i18n.CONSTANT), i18n.get_key(i18n.CONSTANT), "IPO_CONSTANT", 0),
                  ("LINEAR", i18n.get_key(i18n.LINEAR), i18n.get_key(i18n.LINEAR), "IPO_LINEAR", 1),
                  ("BEZIER", i18n.get_key(i18n.BEZIER), i18n.get_key(i18n.BEZIER), "IPO_BEZIER", 2),
                  ("SINE", i18n.get_key(i18n.SINUSOIDAL), i18n.get_key(i18n.SINUSOIDAL), "IPO_SINE", 3),
                  ("QUAD", i18n.get_key(i18n.QUADRATIC), i18n.get_key(i18n.QUADRATIC), "IPO_QUAD", 4),
                  ("CUBIC", i18n.get_key(i18n.CUBIC), i18n.get_key(i18n.CUBIC), "IPO_CUBIC", 5),
                  ("QUART", i18n.get_key(i18n.QUARTIC), i18n.get_key(i18n.QUARTIC), "IPO_QUART", 6),
                  ("QUINT", i18n.get_key(i18n.QUINTIC), i18n.get_key(i18n.QUINTIC), "IPO_QUINT", 7),
                  ("EXPO", i18n.get_key(i18n.EXPONENTIAL), i18n.get_key(i18n.EXPONENTIAL), "IPO_EXPO", 8),
                  ("CIRC", i18n.get_key(i18n.CIRCULAR), i18n.get_key(i18n.CIRCULAR), "IPO_CIRC", 9),
                  ("BACK", i18n.get_key(i18n.BACK), i18n.get_key(i18n.BACK), "IPO_BACK", 10),
                  ("BOUNCE", i18n.get_key(i18n.BOUNCE), i18n.get_key(i18n.BOUNCE), "IPO_BOUNCE", 11),
                  ("ELASTIC", i18n.get_key(i18n.ELASTIC), i18n.get_key(i18n.ELASTIC), "IPO_ELASTIC", 12)]
EASING_ENUMS = [
    ("AUTO", i18n.get_key(i18n.AUTOMATIC_EASING), i18n.get_key(i18n.AUTOMATIC_EASING), "IPO_EASE_IN_OUT", 0),
    ("EASE_IN", i18n.get_key(i18n.EASE_IN), i18n.get_key(i18n.EASE_IN), "IPO_EASE_IN", 1),
    ("EASE_OUT", i18n.get_key(i18n.EASE_OUT), i18n.get_key(i18n.EASE_OUT), "IPO_EASE_OUT", 2),
    ("EASE_IN_OUT", i18n.get_key(i18n.EASE_IN_AND_OUT), i18n.get_key(i18n.EASE_IN_AND_OUT), "IPO_EASE_IN_OUT", 3)]


class KeyframeProperties(PropertyGroup):
    interpolation: EnumProperty(items=INTERPOLATIONS, default="BEZIER", name=i18n.get_key(i18n.INTERPOLATION),
                                description=i18n.get_key(i18n.INTERPOLATION))
    easing: EnumProperty(items=EASING_ENUMS, default="AUTO", name=i18n.get_key(i18n.EASING),
                         description=i18n.get_key(i18n.EASING))


OTHER_TOOLS = [("rename_action", i18n.get_key(i18n.RENAME_ACTION), i18n.get_key(i18n.RENAME_ACTION), 0),
               ("generate_transitions", i18n.get_key(i18n.GENERATE_TRANSITIONS),
                i18n.get_key(i18n.GENERATE_TRANSITIONS_DESCRIPTION), 1),
               ("delete_transitions", i18n.get_key(i18n.DELETE_TRANSITIONS),
                i18n.get_key(i18n.DELETE_TRANSITIONS_DESCRIPTIONS), 2)]
RENAME_ACTION_SOURCE = \
    [("nla_midi_panel", i18n.get_key(i18n.MIDI_PANEL), i18n.get_key(i18n.RENAME_MIDI_PANEL_ACTION_DESCRIPTION), 0),
     ("selected_nla_strip", i18n.get_key(i18n.SELECTED_NLA_STRIP),
      i18n.get_key(i18n.RENAME_SELECTED_NLA_STRIP_ACTION_DESCRIPTION), 1),
     ("selected", i18n.get_key(i18n.SELECT_ACTION), i18n.get_key(i18n.SELECT_THE_ACTION_TO_RENAME), 2)]
TRANSITION_PLACEMENT = [("start", i18n.get_key(i18n.START), i18n.get_key(i18n.TRANSITION_START_DESCRIPTION), 0),
                        ("end", i18n.get_key(i18n.END), i18n.get_key(i18n.TRANSITION_END_DESCRIPTION), 1)]


class OtherToolsPropertyGroup(PropertyGroup):
    selected_tool: EnumProperty(name=i18n.get_key(i18n.TOOL),
                                description=i18n.get_key(i18n.TOOL), items=OTHER_TOOLS,
                                default="rename_action")
    # rename action
    rename_action_source: EnumProperty(name=i18n.get_key(i18n.ACTION_SOURCE),
                                       description=i18n.get_key(i18n.ACTION_SOURCE_DESCRIPTION),
                                       items=RENAME_ACTION_SOURCE,
                                       default="nla_midi_panel")
    selected_rename_action: PointerProperty(type=bpy.types.Action, name=i18n.get_key(i18n.ACTION),
                                            description=i18n.get_key(i18n.THE_ACTION_TO_RENAME))
    # generate transitions
    keyframe_properties: PointerProperty(type=KeyframeProperties)
    limit_transition_length: BoolProperty(name=i18n.get_key(i18n.LIMIT_TRANSITION_LENGTH),
                                          description=i18n.get_key(i18n.LIMIT_TRANSITION_LENGTH),
                                          default=False)
    transition_limit_frames: IntProperty(name=i18n.get_key(i18n.TRANSITION_LENGTH_FRAMES),
                                         description=i18n.get_key(i18n.TRANSITION_LIMIT_FRAMES_DESCRIPTION),
                                         default=10,
                                         min=1)
    transition_offset_frames: IntProperty(name=i18n.get_key(i18n.get_key(i18n.TRANSITION_OFFSET_FRAMES)),
                                          description=i18n.get_key(i18n.TRANSITION_OFFSET_FRAMES_DESCRIPTION),
                                          default=0,
                                          min=0)
    transition_placement: EnumProperty(items=TRANSITION_PLACEMENT, name=i18n.get_key(i18n.PLACEMENT),
                                       description=i18n.get_key(i18n.TRANSITION_PLACEMENT))
    replace_transition_strips: BoolProperty(name=i18n.get_key(i18n.REPLACE_TRANSITION_STRIPS),
                                            description=i18n.get_key(i18n.REPLACE_TRANSITION_STRIPS_DESCRIPTION),
                                            default=False)


# endregion


# Property definitions from a parent class work with multiple inheritance, with one of the classes being PropertyGroup.
# It doesn't work if extending a class that extends PropertyGroup (properties from the parent class are not recognized
# in that case).
class MidiPropertyGroup(MidiPropertyBase, PropertyGroup):
    data_type = MidiDataType.NLA
    # overwrite property from parent class MidiPropertyBase in order to override update function
    notes_list: EnumProperty(items=get_notes_list,
                             name=i18n.get_key(i18n.NOTE),
                             description=i18n.get_key(i18n.NOTE),
                             update=update_notes_list)
    note_action_property: PointerProperty(type=NoteActionProperty)

    instruments: CollectionProperty(type=InstrumentProperty, name=i18n.get_key(i18n.INSTRUMENTS))
    selected_instrument_id: EnumProperty(items=get_instruments, name=i18n.get_key(i18n.INSTRUMENT),
                                         description=i18n.get_key(i18n.SELECT_AN_INSTRUMENT))

    copy_to_instrument_selected_instrument: EnumProperty(items=get_instruments, name=i18n.get_key(i18n.INSTRUMENT),
                                                         description=i18n.get_key(
                                                             i18n.INSTRUMENT_TO_COPY_THE_ACTION_TO))
    copy_to_instrument_selected_note_id: \
        PropertyUtils.note_property(i18n.get_key(i18n.NOTE), i18n.get_key(i18n.NOTE_TO_COPY_THE_ACTION_TO),
                                    get_notes_for_copy_panel,
                                    "copy_to_instrument_selected_note_id", "copy_to_instrument_note_search_string")
    copy_to_instrument_note_search_string: \
        PropertyUtils.note_search_property("copy_to_instrument_selected_note_id",
                                           "copy_to_instrument_note_search_string",
                                           get_notes_for_copy_panel)

    bulk_copy_property: PointerProperty(type=BulkCopyPropertyGroup)

    tempo_settings: PointerProperty(type=TempoPropertyGroup)

    other_tool_property: PointerProperty(type=OtherToolsPropertyGroup)


class MidiCopierVersion(PropertyGroup):
    """
    Stores the version of the midi copier used when in the blend file. Allows for backwards compatibility when
    changing properties.
    """
    major: IntProperty()
    minor: IntProperty()
    revision: IntProperty()
