from typing import Union
from typing import Tuple
import bpy


def operator(string) -> Tuple[str, str]:
    """
    :param string: text that will be passed to Blender's translation
    :return: i18n key for the Operator context
    """
    return "Operator", string


def get_text(i18n_data: Union[str, Tuple[str, str]]) -> str:
    """
    :param i18n_data: i18n key
    :return: text translated by Blender
    """
    if isinstance(i18n_data, str):
        return bpy.app.translations.pgettext_iface(i18n_data)
    else:
        return bpy.app.translations.pgettext_iface(i18n_data[1], i18n_data[0])


def get_text_tip(i18n_data: Union[str, Tuple[str, str]]) -> str:
    """
    :param i18n_data: i18n key
    :return: text translated by Blender
    """
    if isinstance(i18n_data, str):
        return bpy.app.translations.pgettext_tip(i18n_data)
    else:
        return bpy.app.translations.pgettext_tip(i18n_data[1], i18n_data[0])


def get_key(i18n_data: Union[str, Tuple[str, str]]) -> str:
    """
    :param i18n_data: i18n key
    :return: text that will be passed to Blender's translation
    """
    return i18n_data if isinstance(i18n_data, str) else i18n_data[1]


def get_label(i18n_data: Union[str, Tuple[str, str]]) -> str:
    """
    :param i18n_data: i18n key
    :return: text translated by Blender and formatted as a label
    """
    return get_text(i18n_data) + ":"


def concat(*strings, delimiter=" "):
    return delimiter.join(strings)


def parenthetical(string: str) -> str:
    return "(" + string + ")"


ACCELERATION = "Acceleration"
ACTION = "Action"
ACTIONS = "Actions"
ACTIONS_MISSING_OBJECT_OR_ACTION = "Some actions are missing an object or action"
ACTION_DESCRIPTION = "The action to create action strips from"
ACTION_LENGTH_FRAMES = "Action Length (Frames)"
ACTION_LENGTH_FRAMES_DESCRIPTION = "Length of the action, used to determine if the next action overlaps for object duplication. It has no effect on the actual length of the copied action.\nThis option has no effect if \"Sync Length with Notes\" is selected.\nThis will be ignored if it is shorter than the actual length of the action"
ACTION_NAME = "Action name"
ACTION_SOURCE = "Action source"
ACTION_SOURCE_DESCRIPTION = "Where to get the action to rename"
ACTION_TIMING = "Action Timing"
ACTIVE_NLA_TRACK = "Active NLA track"
ADD = "Add"
ADD_ACTION_OP = operator("Add Action")
ADD_ACTION_TO_INSTRUMENT_DESCRIPTION = "Add an action for the selected note"
ADD_A_FILTER = "Add a filter"
ADD_FILTERS = "Add filters"
ADD_FILTERS_DESCRIPTION = "Add filters to exclude notes"
ADD_FILTER_GROUP_DESCRIPTION = "Add a filter group.\nA filter group is a list of filters to be applied when coping the action. The filters in each group will be applied in the order they are defined. The action is copied to notes that match any of the filter groups"
ADD_FILTER_GROUP_OP = operator("Add Filter Group")
ADD_FILTER_OP = operator("Add Filter")
ALL_PITCHES = "All Pitches"
ALL_PITCHES_FILTER_DESCRIPTION = "If selected, the filter group acts on all pitches (ignoring the selected pitch in the midi panel, or igonring the instrument note if this filter is part of an instrument). This is always selected if any of the filters are pitch filters"
ALTERNATION_FILTER_DESCRIPTION = "Filter notes by an alternation pattern. (For example only every fourth note, starting with the third note.)"
ANGLE = "Angle"
ANIMATE = "Animate"
ANIMATE_ALL_INSTRUMENTS = "Animate All Instruments"
ANIMATE_ALL_INSTRUMENTS_OP = operator("Animate All Instruments")
ANIMATE_INSTRUMENT = "Animate Instrument"
ANIMATE_INSTRUMENT_OP = operator("Animate Instrument")
AREA = "Area"
ARMATURE = "Armature"
ARMATURE_TO_ANIMATE = "The armature to animate"
AUTOMATIC_EASING = "Automatic Easing"
BACK = "Back"
BEATS_PER_MINUTE = "Beats per minute"
BEZIER = "Bezier"
BLEND = "Blend"
BLENDING = "Blending"
BLENDING_FOR_OVERLAPPING_STRIPS = "Blending for overlapping strips"
BOUNCE = "Bounce"
BPM = "Bpm"
BRUSH = "Brush"
BRUSH_TO_ANIMATE = "The brush to animate"
BY_FRAMES = "By frames"
CACHE_FILE = "Cache File"
CACHE_FILE_TO_ANIMATE = "The cache file to animate"
CAMERA = "Camera"
CAMERA_TO_ANIMATE = "The camera to animate"
CC_DATA = "CC Data"
CC_TYPE = "CC Type"
CHANGE_FILTER_ORDER = "Change filter order"
CHOOSE_MIDI_FILE_OP = operator("Choose midi file")
CIRCULAR = "Circular"
COLLECTION = "Collection"
COLLECTION_TO_ANIMATE = "The collection to animate"
COMBINE = "Combine"
COMPARISON_OPERATOR = "Comparison Operator"
CONSTANT = "Constant"
COPY_ACTIONS_TO_INSTRUMENT = "Copy actions to the selected instrument"
COPY_ACTIONS_TO_SELECTED_OBJECTS = "Copy actions to Selected Objects"
COPY_ACTION_TO_INSTRUMENT = "Copy action to the selected instrument"
COPY_ACTION_TO_NOTES_DESCRIPTION = "Copy the selected Action to the selected note"
COPY_ACTION_TO_NOTES_OP = operator("Copy Action to Notes")
COPY_ACTION_TO_SELECTED_OBJECTS = "Copy Action to Selected Objects"
COPY_ALONG_PATH = "Copy along path"
COPY_ALONG_PATH_CURVE_DESCRIPTION = "The path of selected objects to animate"
COPY_ALONG_PATH_DESCRIPTION = "Animate selected objects, ordered by a path.\n Each object is animated to a different note, ascending by pitch along the path."
COPY_ALONG_PATH_DOES_NOT_WITH_WORK_TYPE = "Copy along path does not with work type"
COPY_ALONG_PATH_STARTING_NOTE_DESCRIPTION = "The note to use for the first object"
COPY_BY = "Copy by"
COPY_BY_NAME = "Copy by name"
COPY_BY_NOTE_NAME = "Copy by note name"
COPY_BY_NOTE_NAME_DESCRIPTION = "Copy to objects with names beginning or ending with the note (for example A3 notes would be copied to an object named CubeA3 or A3Cube)"
COPY_BY_OBJECT_NAME = "Copy by object name"
COPY_BY_OBJECT_NAME_DESCRIPTION = "Copy notes to selected objects based on the object's name."
COPY_BY_OBJECT_NAME_DOES_NOT_WITH_WORK_TYPE = "Copy by object name does not with work type"
COPY_BY_TRACK_AND_NOTE_NAME = "Copy by track and note name"
COPY_BY_TRACK_AND_NOTE_NAME_DESCRIPTION = "Copy to objects with names beginning or ending with the note and containing selected track name"
COPY_FILE_FROM_DOPESHEET_DESCRIPTION = "Load midi file data from the Grease Pencil Editor"
COPY_FILE_FROM_GRAPH_EDITOR_DESCRIPTION = "Load midi file data from the Graph Editor"
COPY_FILE_FROM_NLA_DESCRIPTION = "Load midi file data from the NLA Editor"
COPY_KEYFRAMES_TO_NOTES_DESCRIPTION = "Copy the selected keyframes to the selected note"
COPY_KEYFRAMES_TO_NOTES_OP = operator("Copy Keyframes to Notes")
COPY_MIDI_FILE_DATA = "Copy midi file data"
COPY_MIDI_FILE_DATA_OP = operator("Copy Midi file data")
COPY_TO_INSTRUMENT = "Copy to Instrument"
COPY_TO_INSTRUMENT_DESCRIPTION = "Copies actions to an instrument if selected, otherwise copies actions directly to NLA strips"
COPY_TO_INSTRUMENT_OP = operator("Copy to Instrument")
COPY_TO_NOTE_END = "Copy to Note End"
COPY_TO_NOTE_END_DESCRIPTION = "Copy the action to the end of the note instead of the beginning"
COPY_TO_SELECTED_OBJECTS_DESCRIPTION = "Copy the action to all selected objects."
COPY_TO_SELECTED_OBJECTS_NOT_VALID_FOR_INSTRUMENTS = "Copy to selected objects (in NLA Midi Panel) not valid for instruments"
COPY_TO_SELECTED_OBJECTS_ONLY = "Copy to selected objects only"
COPY_TO_SELECTED_OBJECTS_ONLY_DESCRIPTION = "If selected, copies to selected objects only. Otherwise copies to any matching objects in the scene."
COPY_TO_SINGLE_TRACK = "Copy to single track"
COPY_TO_SINGLE_TRACK_DESCRIPTION = "If selected, copy actions to a single nla track. Otherwise create a track for each note. This is overwritten for any actions that have an Nla Track"
COULD_NOT_LOAD_MIDI_FILE = "Could not load midi file:"
COUNT = "Count"
CREATE_NEW_INSTRUMENT_DESCRIPTION = "Create a new instrument.  An instrument defines one or many actions for each note"
CREATE_NEW_INSTRUMENT_OP = operator("Create New Instrument")
CUBIC = "Cubic"
CURVE = "Curve"
CURVE_TO_ANIMATE = "The curve to animate"
DELETE = "Delete"
DELETE_ACTION = "Delete Action"
DELETE_ACTION_OP = operator("Delete Action")
DELETE_EXISTING_KEYFRAMES = "Delete existing keyframes"
DELETE_FILTER_GROUP = "Delete Filter Group"
DELETE_FILTER_PRESET = "Delete filter preset"
DELETE_INSTRUMENT_DESCRIPTION = "Delete the selected instrument"
DELETE_INSTRUMENT_OP = operator("Delete Instrument")
DELETE_OP = operator("Delete")
DELETE_SOURCE_KEYFRAMES = "Delete Source Keyframes"
DELETE_SOURCE_KEYFRAMES_DESCRIPTION = "Delete the source keyframes after copying"
DELETE_TRANSITIONS = "Delete transitions"
DELETE_TRANSITIONS_DESCRIPTIONS = "Delete transitions between selected NLA strips on the active NLA track"
DELETE_TRANSITIONS_OP = operator("Delete Transitions")
DISPLAYED_NAME = "Displayed Name"
DISPLAYED_TRACK_NAMES = "Displayed Track Names"
DISPLAYED_TRACK_NAME_DESCRIPTION = "Displayed name of the midi track in selection dropdowns"
DISTANCE_LENGTH = "Distance/Length"
DO_NOT_FILTER_BY_SCALE = "Do not filter by scale"
DO_NOT_TRANSPOSE = "Do not transpose"
DUPLICATE_OBJECT = "Duplicate Object"
DUPLICATE_OBJECT_DESCRIPTION = "Copy the action to a duplicated object"
DUPLICATE_OBJECT_ON_OVERLAP = "Duplicate Object on Overlap"
DUPLICATE_OBJECT_ON_OVERLAP_DESCRIPTION = "Copy the action to a duplicated object if it overlaps another action"
EASE_IN = "Ease In"
EASE_IN_AND_OUT = "Ease In and Out"
EASE_OUT = "Ease Out"
EASING = "Easing"
ELASTIC = "Elastic"
END = "End"
EQUAL_TO = "Equal to"
EVERY = "Every"
EXPONENTIAL = "Exponential"
FILE_TEMPO = "File Tempo"
FILE_TEMPO_DESCRIPTION = "Use the tempo defined by the midi file"
FILE_TICKS_PER_BEAT = "File Ticks per Beat"
FILE_TICKS_PER_BEAT_DESCRIPTION = "Use the ticks per beat defined by the midi file. (Selecting this and changing only the beats per minute should be sufficient for most tempo changes.)"
FILTERS = "Filters"
FILTERS_MAY_PATH_DIFFERENT_PITCHES = "Some actions have filters that may pitch different pitches"
FILTER_BY_SCALE = "Filter by Scale"
FILTER_GROUP = "Filter Group"
FILTER_PRESETS = "Filter Presets"
FILTER_TYPE = "Filter Type"
FIRST_FRAME = "First Frame"
FIRST_FRAME_DESCRIPTION = "The frame corresponding to the beginning of the midi file"
FRAMES = "Frames"
FRAME_OFFSET = "Frame Offset"
FRAME_OFFSET_WHEN_COPYING_STRIPS = "Frame offset when copying strips"
GENERATE_AT_NOTE_END = "Generate at Note End"
GENERATE_AT_NOTE_END_DESCRIPTION = "Generate keyframes at the end of the note instead of the beginning"
GENERATE_KEYFRAMES = "Generate Keyframes"
GENERATE_KEYFRAMES_OP = operator("Generate Keyframes")
GENERATE_TRANSITIONS = "Generate transitions"
GENERATE_TRANSITIONS_DESCRIPTION = "Generate transitions between selected NLA strips on the active NLA track"
GENERATE_TRANSITIONS_OP = operator("Generate Transitions")
GRAPH_EDITOR_LIMIT_TRANSITION_DESCRIPTION = "Limit transition length by placing intermediate keyframes to hold a constant value"
GRAPH_EDITOR_MIDI = "Graph Editor Midi"
GRAPH_EDITOR_TRANSITION_END_DESCRIPTION = "Place transitions directly before the trailing keyframe"
GRAPH_EDITOR_TRANSITION_LENGTH_DESCRIPTION = "Maximum length between transition keyframes"
GRAPH_EDITOR_TRANSITION_START_DESCRIPTION = "Place transitions directly after the leading keyframe"
GREASE_PENCIL = "Grease Pencil"
GREASE_PENCIL_MIDI = "Grease Pencil Midi"
GREASE_PENCIL_ONLY_SELECTED = "Select \"Only Selected\" in the Dope Sheet bar to show the grease pencil midi panel."
GREASE_PENCIL_SKIP_OVERLAPS_DESCRIPTION = "Skip notes if the first frame would be at or before the last frame of the previous note"
GREASE_PENCIL_SYNC_LENGTH_DESCRIPTION = "Scale the copied keyframes' spacing so that the length matches the lengths of the notes they are copied to"
GREASE_PENCIL_TO_ANIMATE = "The grease pencil to animate"
GREATER_THAN = "Greater than"
GREATER_THAN_OR_EQUAL_TO = "Greater than or equal to"
HIGHEST_NOTE = "Highest note"
HOW_TO_HANDLE_OVERLAPPING_ACTIONS = "How to handle overlapping actions"
IMAGE = "Image"
IMAGE_TO_ANIMATE = "The image to animate"
INCLUDE = "Include"
INSTRUMENT = "Instrument"
INSTRUMENTS = "Instruments"
INSTRUMENT_FRAME_OFFSET = "Instrument Frame Offset"
INSTRUMENT_TO_COPY_THE_ACTION_TO = "Instrument to copy the action to"
INTEGER = "Integer"
INTEGER_0_TO_127_INCLUSIVE = "Integer between 0 and 127, inclusive"
INTERPOLATION = "Interpolation"
IN_SCALE = "In scale"
IN_SCALE_DESCRIPTION = "Only include nodes in the selected scale"
KEY = "Key"
KEYFRAME_NOTE_END_DESCRIPTION = "Place keyframes at the end of notes"
KEYFRAME_NOTE_START_AND_END_DESCRIPTION = "Place keyframes at both the start and end of notes"
KEYFRAME_NOTE_START_DESCRIPTION = "Place keyframes at the start of notes"
KEYFRAME_OVERLAP = "Keyframe Overlap"
KEYFRAME_OVERLAP_HANDLING_MODE = "Keyframe overlap handling mode"
KEYFRAME_PLACEMENT = "Keyframe placement"
KEY_TO_ANIMATE = "The key to animate"
LATTICE = "Lattice"
LATTICE_TO_ANIMATE = "The lattice to animate"
LAYER = "Layer"
LENGTH_FRAMES = "Length (frames)"
LESS_THAN = "Less than"
LESS_THAN_OR_EQUAL_TO = "Less than or equal to"
LIGHT = "Light"
LIGHT_PROBE = "Light Probe"
LIGHT_PROBE_TO_ANIMATE = "The light probe to animate"
LIGHT_TO_ANIMATE = "The light to animate"
LIMIT_TRANSITION_LENGTH = "Limit transition length"
LINEAR = "Linear"
LOAD_MIN_AND_MAX_VALUES_OP = operator("Load min and max values")
LOAD_MIN_MAX_DESCRIPTION = "Load minimum and maximum vales from the Midi Track"
LOWEST_NOTE = "Lowest Note"
MAJOR_SCALE = "Major Scale"
MAP_TO_MAX = "Map to max"
MAP_TO_MAX_KEYFRAME_DESCRIPTION = "Value from midi file to map to maximum keyframe value"
MAP_TO_MIN = "Map to min"
MAP_TO_MIN_KEYFRAME_DESCRIPTION = "Value from midi file to map to minimum keyframe value"
MASK = "Mask"
MASK_TO_ANIMATE = "The mask to animate"
MASS = "Mass"
MATERIAL = "Material"
MATERIAL_TO_ANIMATE = "The material to animate"
MAX = "Max"
MAXIMUM_KEYFRAME_VALUE_TO_GENERATE = "Maximum keyframe value to generate"
MAX_NOTE = "Max note"
MESH = "Mesh"
MESH_TO_ANIMATE = "The mesh to animate"
METABALL = "Metaball"
METABALL_TO_ANIMATE = "The metaball to animate"
MIDDLE_C = "Middle C"
MIDDLE_C_DESCRIPTION = "The note corresponding to middle C (midi note 60)"
MIDI = "Midi"
MIDI_FILE = "Midi File"
MIDI_INSTRUMENTS = "Midi Instruments"
MIDI_NOTE = "Midi note"
MIDI_PANEL = "Midi Panel"
MIDI_SETTINGS = "Midi Settings"
MIDI_TRACK = "Midi Track"
MIDI_TRACKS = "Midi Tracks"
MIDI_TRACK_DESCRIPTION = "Name of the track from the midi file"
MIN = "Min"
MINIMUM_KEYFRAME_VALUE_TO_GENERATE = "Minimum keyframe value to generate"
MINUS_OCTAVE = "- octave"
MINUS_STEP = "- step"
MIN_NOTE = "Min note"
MOVIE_CLIP = "Movie Clip"
MOVIE_CLIP_TO_ANIMATE = "The movie clip to animate"
MULTIPLY = "Multiply"
NAME = "Name"
NEW = "New"
NEW_FILTER_PRESET = "New filter preset"
NEXT_FRAME = "Next frame"
NEXT_FRAME_DESCRIPTION = "If an existing keyframe is on the same frame, place the generated keyframe on the frame after the existing keyframe. If the frame after also has a keyframe, the generated keyframe will be skipped"
NLA_MIDI = "NLA Midi"
NLA_MIDI_INSTRUMENTS = "NLA Midi Instruments"
NLA_TRACK = "Nla Track"
NLA_TRACK_DESCRIPTION = "Name of the NLA Track that action strips will be placed on.\nA track name will be automatically generated if this is blank"
NLA_TRACK_INSTRUMENT_DESCRIPTION = "Name of the nla track to copy actions to. A name will be generated of this field is blank. This field is not used if \"Copy to Single Track\" is not selected"
NODE_TREE = "Node Tree"
NONE = "None"
NON_NEGATIVE_INT = "Non Negative Int"
NON_NEGATIVE_INTEGER = "Non-negative integer"
NON_NEGATIVE_NUMBER = "Non negative number"
NOTE = "Note"
NOTES = "Notes"
NOTES_IN_TRACK = "Notes in Track"
NOTE_END = "Note End"
NOTE_FILTERS = "Note Filters"
NOTE_FILTER_GROUPS = "Note Filter Groups"
NOTE_LENGTH = "Note Length"
NOTE_LENGTH_FILTER_DESCRIPTION = "Filter notes by length"
NOTE_LENGTH_IN_FRAMES = "Note Length in Frames"
NOTE_OVERLAP = "Note overlap"
NOTE_OVERLAP_INCLUDE_KEYFRAME_DESCRIPTION = "Generate keyframes for notes that overlap other notes"
NOTE_OVERLAP_SKIP_KEYFRAME_DESCRIPTION = "Skip notes if the first frame would be before the last frame of the previous note"
NOTE_PROPERTY = "Note Property"
NOTE_SEARCH_DESCRIPTION = "Enter a note name or midi note number to select a note"
NOTE_START = "Note Start"
NOTE_START_AND_END = "Note Start and End"
NOTE_TO_COPY_THE_ACTION_TO = "Note to copy the action to"
NOT_IN_SCALE = "Not in scale"
NOT_IN_SCALE_DESCRIPTION = "Only include notes that are not in the selected scale"
NO_ACTION_SELECTED = "No action selected"
NO_ACTION_SELECTED_IN_MLA_MIDI_PANEL = "No action selected (in NLA Midi Panel)"
NO_FILTER = "No filter"
NO_F_CURVE_SELECTED = "No F-Curve selected"
NO_INSTRUMENT_SELECTED = "No instrument selected"
NO_MIDI_FILE_SELECTED = "No Midi File Selected"
NO_NLA_TRACK_SELECTED = "No NLA track selected"
NO_PATH_SELECTED = "No path selected"
NO_PRESET_SELECTED = "No preset selected"
OBJECT = "Object"
OBJECT_TO_ANIMATE = "The object to animate"
ONLY_KEYFRAME_NOTES_IN_SELECTED_TRACK_DESCRIPTION = "Only calculate keyframes based on notes in the selected track"
ONLY_NOTES_IN_SELECTED_TRACK = "Only Notes in Selected Track"
ONLY_NOTES_IN_SELECTED_TRACK_DESCRIPTION = "Only copy to notes in the selected Track in the NLA Midi Panel"
ON_CC_CHANGE = "On CC change"
OTHER_TOOLS = "Other Tools"
OVERLAP = "Overlap"
OVERLAP_BLEND_DESCRIPTION = "Place the action on a new track above the existing action"
OVERLAP_BY_FRAMES_DESCRIPTION = "If selected, calculate overlaps using the same length in frames for every note"
OVERLAP_FILTER_DESCRIPTION = "Filter by note overlaps.\nLayer is the location of the note in the overlap starting from the lowest note. Lowest note is layer 1.\nCount is the number of notes in the overlap. A note by itself has count 1."
OVERLAP_SKIP_DESCRIPTION = "Skip keyframe if an existing keyframe is on the same frame"
PAINTCURVE = "Paintcurve"
PAINTCURVE_TO_ANIMATE = "The paintcurve to animate"
PALETTE = "Palette"
PALETTE_TO_ANIMATE = "The palette to animate"
PARTICLE_SETTINGS = "Particle Settings"
PARTICLE_SETTINGS_TO_ANIMATE = "The particle settings to animate"
PATH = "Path"
PITCH = "Pitch"
PITCH_FILTER_DESCRIPTION = "Filter by the note's pitch. (This overrides the selected note.)"
PLACEMENT = "Placement"
PLUS_OCTAVE = "+ octave"
PLUS_STEP = "+ step"
POSITIVE_INT = "Positive Int"
POSITIVE_INTEGER = "Positive Integer"
POWER = "Power"
PRESET = "Preset"
PREVIOUS_FRAME = "Previous frame"
PREVIOUS_FRAME_DESCRIPTION = "If an existing keyframe is on the same frame, place the generated keyframe on the frame before the existing keyframe. If the frame before also has a keyframe, the generated keyframe will be skipped"
PROPERTIES = "Properties"
PROPERTY_TYPE = "Property Type"
QUADRATIC = "Quadratic"
QUARTIC = "Quartic"
QUICK_COPY_TOOL = "Quick copy tool"
QUICK_COPY_TOOLS = "Quick Copy Tools"
QUINTIC = "Quintic"
RELATIVE_PATH = "Relative Path"
RELATIVE_START_TIME = "Relative Start Time"
RELATIVE_START_TIME_FILTER_DESCRIPTION = "Filter notes by start time (relative to the start of the midi file)"
RELOAD_BLEND_FILE_FOR_OPTIONS = "Reload the blend file to see options here."
REMOVE_FILTER = "Remove filter"
REMOVE_FILTER_GROUP_OP = operator("Remove Filter Group")
REMOVE_FILTER_OP = operator("Remove Filter")
RENAME_ACTION = "Rename Action"
RENAME_MIDI_PANEL_ACTION_DESCRIPTION = "Rename the action selected in the midi panel"
RENAME_SELECTED_NLA_STRIP_ACTION_DESCRIPTION = "Rename the action from the selected NLA strip"
REORDER_FILTER_OP = operator("Reorder Filter")
REPEAT = "Repeat"
REPEAT_ACTION_LENGTH_DESCRIPTION = "Repeat action (or truncate action if shorter than the note length)"
REPLACE = "Replace"
REPLACE_KEYFRAME_DESCRIPTION = "Replace existing keyframe if on the same frame"
REPLACE_TRANSITION_STRIPS = "Replace transition strips"
REPLACE_TRANSITION_STRIPS_DESCRIPTION = "Replace existing transition strips"
SAVE = "Save"
SAVE_FILTER_PRESET = "Save filter preset"
SCALE = "Scale"
SCALE_ACTION_LENGTH = "Scale Action Length"
SCALE_FACTOR = "Scale Factor"
SCALE_FACTOR_DESCRIPTION = "Scale factor for scaling to the note's length. For example, a scale factor of 1 will scale to the note's length, a scale factor of 2 will scale to twice the note's length, and a scale factor of 0.5 will scale to half the note's length"
SCENE = "Scene"
SCENE_TO_ANIMATE = "The scene to animate"
SEARCH = "Search"
SECONDS = "Seconds"
SELECTED = "Selected"
SELECTED_F_CURVE = "Selected F-Curve"
SELECTED_F_CURVES = "Selected F-Curves"
SELECTED_MIDI_FILE = "Selected Midi File"
SELECTED_MIDI_TRACK = "Selected Midi Track"
SELECTED_NLA_STRIP = "Selected NLA Strip"
SELECTED_NOTE_FILTER_ENUM_DESCRIPTION = "The selected pitch in the Midi panel, or the pitch corresponding to the instrument note if this filter is part of an instrument"
SELECT_ACTION = "Select Action"
SELECT_AN_F_CURVE_IN_THE_GRAPH_EDITOR = "Select an F-Curve in the Graph Editor"
SELECT_AN_INSTRUMENT = "Select an instrument"
SELECT_A_FILTER_PRESET = "Select a filter preset"
SELECT_MIDI_FILE_DESCRIPTION = "Select a midi file"
SELECT_THE_ACTION_TO_RENAME = "Select the action to rename"
SHOW_OTHER_TOOLS_PANEL = "Show Other Tools panel"
SHOW_OTHER_TOOLS_PANEL_IF_ENABLED = "Show Other Tools panel if enabled"
SINUSOIDAL = "Sinusoidal"
SKIP = "Skip"
SKIP_KEYFRAME_DESCRIPTION = "Skip keyframe if an existing keyframe is on the same frame"
SKIP_OVERLAPS = "Skip Overlaps"
SOUND = "Sound"
SOUND_TO_ANIMATE = "The sound to animate"
SPEAKER = "Speaker"
SPEAKER_TO_ANIMATE = "The speaker to animate"
START = "Start"
STARTING_NOTE = "Starting Note"
START_TIME = "Start Time"
START_TIME_FILTER_DESCRIPTION = "Filter notes by start time"
SUBTRACT = "Subtract"
SYNC_LENGTH_WITH_NOTES = "Sync Length with Notes"
SYNC_LENGTH_WITH_NOTES_DESCRIPTION = "Scale the copied NLA strips so that their lengths match the lengths of the notes they are copied to"
TEMPERATURE = "Temperature"
TEXT = "Text"
TEXTURE = "Texture"
TEXTURE_TO_ANIMATE = "The texture to animate"
TEXT_TO_ANIMATE = "The text to animate"
THE_ACTION_TO_RENAME = "The action to rename"
THE_NODE_TREE_TO_ANIMATE = "The node tree to animate"
TICKS_PER_BEAT = "Ticks per beat"
TIME_UNIT = "Time unit"
TOOL = "Tool"
TRACK = "Track"
TRANSITION_END_DESCRIPTION = "Place transitions right before the trailing action"
TRANSITION_LENGTH_FRAMES = "Transition length (frames)"
TRANSITION_LIMIT_FRAMES_DESCRIPTION = "Generate transitions no longer than this length in frames"
TRANSITION_OFFSET_FRAMES = "Transition offset (frames)"
TRANSITION_OFFSET_FRAMES_DESCRIPTION = "Offset transition by up to this many frames"
TRANSITION_PLACEMENT = "Transition Placement"
TRANSITION_START_DESCRIPTION = "Place transitions right after the leading action"
TRANSPOSE = "Transpose"
TRANSPOSE_ALL = "Transpose all"
TRANSPOSE_ALL_FILTERS = "Transpose all filters"
TRANSPOSE_EXCEPT_ALL_INCLUSIVE = "Transpose all except all-inclusive"
TRANSPOSE_EXCEPT_ALL_INCLUSIVE_DESCRIPTION = "Transpose all filters except for filters than include every pitch"
TRANSPOSE_FILTERS = "Transpose Filters"
TRANSPOSE_FILTERS_DESCRIPTION = "Set how pitch filters will be transposed"
TRANSPOSE_IF_POSSIBLE = "Transpose if possible"
TRANSPOSE_IF_POSSIBLE_DESCRIPTION = "Transpose filters if possible. Does not transpose filters that can't be transposed due to range constraints"
TRANSPOSE_IF_POSSIBLE_EXCEPT_ALL_DESCRIPTION = "Transpose filters if possible. Does not transpose filters that can't be transposed due to range constraints. Does not transpose filters than include every pitch"
TRANSPOSE_IF_POSSIBLE_EXCEPT_ALL_INCLUSIVE = "Transpose if possible except all-inclusive"
TRANSPOSE_INSTRUMENT = "Transpose Instrument"
TRANSPOSE_INSTRUMENT_OP = operator("Transpose Instrument")
TRANSPOSE_STEPS = "Transpose Steps"
TYPE = "Type"
TYPE_DESCRIPTION = "Type of object to apply the action to"
UNIT_TYPE = "Unit Type"
USE_RELATIVE_PATH_TO_MIDI_FILE = "Use relative path to midi file"
VELOCITY = "Velocity"
VELOCITY_FILTER_DESCRIPTION = "Filter notes by velocity"
VOLUME = "Volume"
VOLUME_TO_ANIMATE = "The volume to animate"
WORLD = "World"
WORLD_TO_ANIMATE = "The world to animate"
