if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from . import i18n

import bpy

i18n_es = {
    i18n.ACCELERATION: None,
    i18n.ACTION: None,
    i18n.ACTIONS: None,
    i18n.ACTIONS_MISSING_OBJECT_OR_ACTION: None,
    i18n.ACTION_DESCRIPTION: None,
    i18n.ACTION_LENGTH_FRAMES: None,
    i18n.ACTION_LENGTH_FRAMES_DESCRIPTION: None,
    i18n.ACTION_NAME: None,
    i18n.ACTION_SOURCE: None,
    i18n.ACTION_SOURCE_DESCRIPTION: None,
    i18n.ACTION_TIMING: None,
    i18n.ACTIVE_NLA_TRACK: None,
    i18n.ADD: None,
    i18n.ADD_ACTION_OP: None,
    i18n.ADD_ACTION_TO_INSTRUMENT_DESCRIPTION: None,
    i18n.ADD_A_FILTER: None,
    i18n.ADD_FILTERS: None,
    i18n.ADD_FILTERS_DESCRIPTION: None,
    i18n.ADD_FILTER_GROUP_DESCRIPTION: None,
    i18n.ADD_FILTER_GROUP_OP: None,
    i18n.ADD_FILTER_OP: None,
    i18n.ALTERNATION_FILTER_DESCRIPTION: None,
    i18n.ANGLE: None,
    i18n.ANIMATE: None,
    i18n.ANIMATE_ALL_INSTRUMENTS: None,
    i18n.ANIMATE_ALL_INSTRUMENTS_OP: None,
    i18n.ANIMATE_INSTRUMENT: None,
    i18n.ANIMATE_INSTRUMENT_OP: None,
    i18n.AREA: None,
    i18n.ARMATURE: None,
    i18n.ARMATURE_TO_ANIMATE: None,
    i18n.AUTOMATIC_EASING: None,
    i18n.BACK: None,
    i18n.BEATS_PER_MINUTE: None,
    i18n.BEZIER: None,
    i18n.BLEND: None,
    i18n.BLENDING: None,
    i18n.BLENDING_FOR_OVERLAPPING_STRIPS: None,
    i18n.BOUNCE: None,
    i18n.BPM: None,
    i18n.BRUSH: None,
    i18n.BRUSH_TO_ANIMATE: None,
    i18n.BY_FRAMES: None,
    i18n.CACHE_FILE: None,
    i18n.CACHE_FILE_TO_ANIMATE: None,
    i18n.CAMERA: None,
    i18n.CAMERA_TO_ANIMATE: None,
    i18n.CC_DATA: None,
    i18n.CC_TYPE: None,
    i18n.CHANGE_FILTER_ORDER: None,
    i18n.CHOOSE_MIDI_FILE_OP: "Elegir archivo midi",
    i18n.CIRCULAR: None,
    i18n.COLLECTION: None,
    i18n.COLLECTION_TO_ANIMATE: None,
    i18n.COMBINE: None,
    i18n.COMPARISON_OPERATOR: None,
    i18n.CONSTANT: None,
    i18n.COPY_ACTIONS_TO_INSTRUMENT: None,
    i18n.COPY_ACTIONS_TO_SELECTED_OBJECTS: None,
    i18n.COPY_ACTION_TO_INSTRUMENT: None,
    i18n.COPY_ACTION_TO_NOTES_DESCRIPTION: None,
    i18n.COPY_ACTION_TO_NOTES_OP: None,
    i18n.COPY_ACTION_TO_SELECTED_OBJECTS: "Copiar acción a objetos seleccionados",
    i18n.COPY_ALONG_PATH: None,
    i18n.COPY_ALONG_PATH_CURVE_DESCRIPTION: None,
    i18n.COPY_ALONG_PATH_DESCRIPTION: None,
    i18n.COPY_ALONG_PATH_DOES_NOT_WITH_WORK_TYPE: None,
    i18n.COPY_ALONG_PATH_STARTING_NOTE_DESCRIPTION: None,
    i18n.COPY_BY: None,
    i18n.COPY_BY_NAME: None,
    i18n.COPY_BY_NOTE_NAME: None,
    i18n.COPY_BY_NOTE_NAME_DESCRIPTION: None,
    i18n.COPY_BY_OBJECT_NAME: None,
    i18n.COPY_BY_OBJECT_NAME_DESCRIPTION: None,
    i18n.COPY_BY_OBJECT_NAME_DOES_NOT_WITH_WORK_TYPE: None,
    i18n.COPY_BY_TRACK_AND_NOTE_NAME: None,
    i18n.COPY_BY_TRACK_AND_NOTE_NAME_DESCRIPTION: None,
    i18n.COPY_FILE_FROM_DOPESHEET_DESCRIPTION: None,
    i18n.COPY_FILE_FROM_GRAPH_EDITOR_DESCRIPTION: None,
    i18n.COPY_FILE_FROM_NLA_DESCRIPTION: None,
    i18n.COPY_KEYFRAMES_TO_NOTES_DESCRIPTION: None,
    i18n.COPY_KEYFRAMES_TO_NOTES_OP: None,
    i18n.COPY_MIDI_FILE_DATA: None,
    i18n.COPY_MIDI_FILE_DATA_OP: None,
    i18n.COPY_TO_INSTRUMENT: None,
    i18n.COPY_TO_INSTRUMENT_DESCRIPTION: None,
    i18n.COPY_TO_INSTRUMENT_OP: None,
    i18n.COPY_TO_NOTE_END: None,
    i18n.COPY_TO_NOTE_END_DESCRIPTION: None,
    i18n.COPY_TO_SELECTED_OBJECTS_DESCRIPTION: None,
    i18n.COPY_TO_SELECTED_OBJECTS_NOT_VALID_FOR_INSTRUMENTS: None,
    i18n.COPY_TO_SELECTED_OBJECTS_ONLY: None,
    i18n.COPY_TO_SELECTED_OBJECTS_ONLY_DESCRIPTION: None,
    i18n.COPY_TO_SINGLE_TRACK: None,
    i18n.COPY_TO_SINGLE_TRACK_DESCRIPTION: None,
    i18n.COULD_NOT_LOAD_MIDI_FILE: None,
    i18n.COUNT: None,
    i18n.CREATE_NEW_INSTRUMENT_DESCRIPTION: None,
    i18n.CREATE_NEW_INSTRUMENT_OP: None,
    i18n.CUBIC: None,
    i18n.CURVE: None,
    i18n.CURVE_TO_ANIMATE: None,
    i18n.DELETE: None,
    i18n.DELETE_ACTION: None,
    i18n.DELETE_ACTION_OP: None,
    i18n.DELETE_EXISTING_KEYFRAMES: None,
    i18n.DELETE_FILTER_GROUP: None,
    i18n.DELETE_FILTER_PRESET: None,
    i18n.DELETE_INSTRUMENT_DESCRIPTION: None,
    i18n.DELETE_INSTRUMENT_OP: None,
    i18n.DELETE_OP: None,
    i18n.DELETE_SOURCE_KEYFRAMES: None,
    i18n.DELETE_SOURCE_KEYFRAMES_DESCRIPTION: None,
    i18n.DELETE_TRANSITIONS: None,
    i18n.DELETE_TRANSITIONS_DESCRIPTIONS: None,
    i18n.DELETE_TRANSITIONS_OP: None,
    i18n.DISPLAYED_NAME: None,
    i18n.DISPLAYED_TRACK_NAMES: None,
    i18n.DISPLAYED_TRACK_NAME_DESCRIPTION: None,
    i18n.DISTANCE_LENGTH: None,
    i18n.DO_NOT_FILTER_BY_SCALE: None,
    i18n.DO_NOT_TRANSPOSE: None,
    i18n.DUPLICATE_OBJECT: None,
    i18n.DUPLICATE_OBJECT_DESCRIPTION: None,
    i18n.DUPLICATE_OBJECT_ON_OVERLAP: None,
    i18n.DUPLICATE_OBJECT_ON_OVERLAP_DESCRIPTION: None,
    i18n.EASE_IN: None,
    i18n.EASE_IN_AND_OUT: None,
    i18n.EASE_OUT: None,
    i18n.EASING: None,
    i18n.ELASTIC: None,
    i18n.END: None,
    i18n.EQUAL_TO: None,
    i18n.EVERY: None,
    i18n.EXPONENTIAL: None,
    i18n.FILE_TEMPO: None,
    i18n.FILE_TEMPO_DESCRIPTION: None,
    i18n.FILE_TICKS_PER_BEAT: None,
    i18n.FILE_TICKS_PER_BEAT_DESCRIPTION: None,
    i18n.FILTERS: None,
    i18n.FILTERS_MAY_PATH_DIFFERENT_PITCHES: None,
    i18n.FILTER_BY_SCALE: None,
    i18n.FILTER_GROUP: None,
    i18n.FILTER_PRESETS: None,
    i18n.FILTER_TYPE: None,
    i18n.FIRST_FRAME: None,
    i18n.FIRST_FRAME_DESCRIPTION: None,
    i18n.FRAMES: None,
    i18n.FRAME_OFFSET: None,
    i18n.FRAME_OFFSET_WHEN_COPYING_STRIPS: None,
    i18n.GENERATE_AT_NOTE_END: None,
    i18n.GENERATE_AT_NOTE_END_DESCRIPTION: None,
    i18n.GENERATE_KEYFRAMES: None,
    i18n.GENERATE_KEYFRAMES_OP: None,
    i18n.GENERATE_TRANSITIONS: None,
    i18n.GENERATE_TRANSITIONS_DESCRIPTION: None,
    i18n.GENERATE_TRANSITIONS_OP: None,
    i18n.GRAPH_EDITOR_LIMIT_TRANSITION_DESCRIPTION: None,
    i18n.GRAPH_EDITOR_MIDI: None,
    i18n.GRAPH_EDITOR_TRANSITION_END_DESCRIPTION: None,
    i18n.GRAPH_EDITOR_TRANSITION_LENGTH_DESCRIPTION: None,
    i18n.GRAPH_EDITOR_TRANSITION_START_DESCRIPTION: None,
    i18n.GREASE_PENCIL: None,
    i18n.GREASE_PENCIL_MIDI: None,
    i18n.GREASE_PENCIL_ONLY_SELECTED: None,
    i18n.GREASE_PENCIL_SKIP_OVERLAPS_DESCRIPTION: None,
    i18n.GREASE_PENCIL_SYNC_LENGTH_DESCRIPTION: None,
    i18n.GREASE_PENCIL_TO_ANIMATE: None,
    i18n.GREATER_THAN: None,
    i18n.GREATER_THAN_OR_EQUAL_TO: None,
    i18n.HIGHEST_NOTE: None,
    i18n.HOW_TO_HANDLE_OVERLAPPING_ACTIONS: None,
    i18n.IMAGE: None,
    i18n.IMAGE_TO_ANIMATE: None,
    i18n.INCLUDE: None,
    i18n.INSTRUMENT: None,
    i18n.INSTRUMENTS: None,
    i18n.INSTRUMENT_FRAME_OFFSET: None,
    i18n.INSTRUMENT_TO_COPY_THE_ACTION_TO: None,
    i18n.INTEGER: None,
    i18n.INTEGER_0_TO_127_INCLUSIVE: None,
    i18n.INTERPOLATION: None,
    i18n.IN_SCALE: None,
    i18n.IN_SCALE_DESCRIPTION: None,
    i18n.KEY: None,
    i18n.KEYFRAME_NOTE_END_DESCRIPTION: None,
    i18n.KEYFRAME_NOTE_START_AND_END_DESCRIPTION: None,
    i18n.KEYFRAME_NOTE_START_DESCRIPTION: None,
    i18n.KEYFRAME_OVERLAP: None,
    i18n.KEYFRAME_OVERLAP_HANDLING_MODE: None,
    i18n.KEYFRAME_PLACEMENT: None,
    i18n.KEY_TO_ANIMATE: None,
    i18n.LATTICE: None,
    i18n.LATTICE_TO_ANIMATE: None,
    i18n.LAYER: None,
    i18n.LENGTH_FRAMES: None,
    i18n.LESS_THAN: None,
    i18n.LESS_THAN_OR_EQUAL_TO: None,
    i18n.LIGHT: None,
    i18n.LIGHT_PROBE: None,
    i18n.LIGHT_PROBE_TO_ANIMATE: None,
    i18n.LIGHT_TO_ANIMATE: None,
    i18n.LIMIT_TRANSITION_LENGTH: None,
    i18n.LINEAR: None,
    i18n.LOAD_MIN_AND_MAX_VALUES_OP: None,
    i18n.LOAD_MIN_MAX_DESCRIPTION: None,
    i18n.LOWEST_NOTE: None,
    i18n.MAJOR_SCALE: None,
    i18n.MAP_TO_MAX: None,
    i18n.MAP_TO_MAX_KEYFRAME_DESCRIPTION: None,
    i18n.MAP_TO_MIN: None,
    i18n.MAP_TO_MIN_KEYFRAME_DESCRIPTION: None,
    i18n.MASK: None,
    i18n.MASK_TO_ANIMATE: None,
    i18n.MASS: None,
    i18n.MATERIAL: None,
    i18n.MATERIAL_TO_ANIMATE: None,
    i18n.MAX: None,
    i18n.MAXIMUM_KEYFRAME_VALUE_TO_GENERATE: None,
    i18n.MAX_NOTE: None,
    i18n.MESH: None,
    i18n.MESH_TO_ANIMATE: None,
    i18n.METABALL: None,
    i18n.METABALL_TO_ANIMATE: None,
    i18n.MIDDLE_C: None,
    i18n.MIDDLE_C_DESCRIPTION: None,
    i18n.MIDI: None,
    i18n.MIDI_FILE: None,
    i18n.MIDI_INSTRUMENTS: None,
    i18n.MIDI_NOTE: None,
    i18n.MIDI_PANEL: None,
    i18n.MIDI_SETTINGS: None,
    i18n.MIDI_TRACK: None,
    i18n.MIDI_TRACKS: None,
    i18n.MIDI_TRACK_DESCRIPTION: None,
    i18n.MIN: None,
    i18n.MINIMUM_KEYFRAME_VALUE_TO_GENERATE: None,
    i18n.MINUS_OCTAVE: None,
    i18n.MINUS_STEP: None,
    i18n.MIN_NOTE: None,
    i18n.MOVIE_CLIP: None,
    i18n.MOVIE_CLIP_TO_ANIMATE: None,
    i18n.MULTIPLY: None,
    i18n.NAME: None,
    i18n.NEW: None,
    i18n.NEW_FILTER_PRESET: None,
    i18n.NEXT_FRAME: None,
    i18n.NEXT_FRAME_DESCRIPTION: None,
    i18n.NLA_MIDI: None,
    i18n.NLA_MIDI_INSTRUMENTS: None,
    i18n.NLA_TRACK: None,
    i18n.NLA_TRACK_DESCRIPTION: None,
    i18n.NLA_TRACK_INSTRUMENT_DESCRIPTION: None,
    i18n.NODE_TREE: None,
    i18n.NONE: None,
    i18n.NON_NEGATIVE_INT: None,
    i18n.NON_NEGATIVE_INTEGER: None,
    i18n.NON_NEGATIVE_NUMBER: None,
    i18n.NOTE: None,
    i18n.NOTES: None,
    i18n.NOTES_IN_TRACK: None,
    i18n.NOTE_END: None,
    i18n.NOTE_FILTERS: None,
    i18n.NOTE_FILTER_GROUPS: None,
    i18n.NOTE_LENGTH: None,
    i18n.NOTE_LENGTH_FILTER_DESCRIPTION: None,
    i18n.NOTE_LENGTH_IN_FRAMES: None,
    i18n.NOTE_OVERLAP: None,
    i18n.NOTE_OVERLAP_INCLUDE_KEYFRAME_DESCRIPTION: None,
    i18n.NOTE_OVERLAP_SKIP_KEYFRAME_DESCRIPTION: None,
    i18n.NOTE_PROPERTY: None,
    i18n.NOTE_SEARCH_DESCRIPTION: None,
    i18n.NOTE_START: None,
    i18n.NOTE_START_AND_END: None,
    i18n.NOTE_TO_COPY_THE_ACTION_TO: None,
    i18n.NOT_IN_SCALE: None,
    i18n.NOT_IN_SCALE_DESCRIPTION: None,
    i18n.NO_ACTION_SELECTED: None,
    i18n.NO_ACTION_SELECTED_IN_MLA_MIDI_PANEL: None,
    i18n.NO_FILTER: None,
    i18n.NO_F_CURVE_SELECTED: None,
    i18n.NO_INSTRUMENT_SELECTED: None,
    i18n.NO_MIDI_FILE_SELECTED: None,
    i18n.NO_NLA_TRACK_SELECTED: None,
    i18n.NO_PATH_SELECTED: None,
    i18n.NO_PRESET_SELECTED: None,
    i18n.OBJECT: None,
    i18n.OBJECT_TO_ANIMATE: None,
    i18n.ONLY_KEYFRAME_NOTES_IN_SELECTED_TRACK_DESCRIPTION: None,
    i18n.ONLY_NOTES_IN_SELECTED_TRACK: None,
    i18n.ONLY_NOTES_IN_SELECTED_TRACK_DESCRIPTION: None,
    i18n.ON_CC_CHANGE: None,
    i18n.OTHER_TOOLS: None,
    i18n.OVERLAP: None,
    i18n.OVERLAP_BLEND_DESCRIPTION: None,
    i18n.OVERLAP_BY_FRAMES_DESCRIPTION: None,
    i18n.OVERLAP_FILTER_DESCRIPTION: None,
    i18n.OVERLAP_SKIP_DESCRIPTION: None,
    i18n.PAINTCURVE: None,
    i18n.PAINTCURVE_TO_ANIMATE: None,
    i18n.PALETTE: None,
    i18n.PALETTE_TO_ANIMATE: None,
    i18n.PARTICLE_SETTINGS: None,
    i18n.PARTICLE_SETTINGS_TO_ANIMATE: None,
    i18n.PATH: None,
    i18n.PITCH: None,
    i18n.PITCH_FILTER_DESCRIPTION: None,
    i18n.PLACEMENT: None,
    i18n.PLUS_OCTAVE: None,
    i18n.PLUS_STEP: None,
    i18n.POSITIVE_INT: None,
    i18n.POSITIVE_INTEGER: None,
    i18n.POWER: None,
    i18n.PRESET: None,
    i18n.PREVIOUS_FRAME: None,
    i18n.PREVIOUS_FRAME_DESCRIPTION: None,
    i18n.PROPERTIES: None,
    i18n.PROPERTY_TYPE: None,
    i18n.QUADRATIC: None,
    i18n.QUARTIC: None,
    i18n.QUICK_COPY_TOOL: None,
    i18n.QUICK_COPY_TOOLS: None,
    i18n.QUINTIC: None,
    i18n.RELATIVE_START_TIME: None,
    i18n.RELATIVE_START_TIME_FILTER_DESCRIPTION: None,
    i18n.RELOAD_BLEND_FILE_FOR_OPTIONS: None,
    i18n.REMOVE_FILTER: None,
    i18n.REMOVE_FILTER_GROUP_OP: None,
    i18n.REMOVE_FILTER_OP: None,
    i18n.RENAME_ACTION: None,
    i18n.RENAME_MIDI_PANEL_ACTION_DESCRIPTION: None,
    i18n.RENAME_SELECTED_NLA_STRIP_ACTION_DESCRIPTION: None,
    i18n.REORDER_FILTER_OP: None,
    i18n.REPEAT: None,
    i18n.REPEAT_ACTION_LENGTH_DESCRIPTION: None,
    i18n.REPLACE: None,
    i18n.REPLACE_KEYFRAME_DESCRIPTION: None,
    i18n.REPLACE_TRANSITION_STRIPS: None,
    i18n.REPLACE_TRANSITION_STRIPS_DESCRIPTION: None,
    i18n.SAVE: None,
    i18n.SAVE_FILTER_PRESET: None,
    i18n.SCALE: None,
    i18n.SCALE_ACTION_LENGTH: None,
    i18n.SCALE_FACTOR: None,
    i18n.SCALE_FACTOR_DESCRIPTION: None,
    i18n.SCENE: None,
    i18n.SCENE_TO_ANIMATE: None,
    i18n.SEARCH: None,
    i18n.SECONDS: None,
    i18n.SELECTED: None,
    i18n.SELECTED_F_CURVE: None,
    i18n.SELECTED_F_CURVES: None,
    i18n.SELECTED_MIDI_FILE: None,
    i18n.SELECTED_MIDI_TRACK: None,
    i18n.SELECTED_NLA_STRIP: None,
    i18n.SELECTED_NOTE_FILTER_ENUM_DESCRIPTION: None,
    i18n.SELECT_ACTION: None,
    i18n.SELECT_AN_F_CURVE_IN_THE_GRAPH_EDITOR: None,
    i18n.SELECT_AN_INSTRUMENT: None,
    i18n.SELECT_A_FILTER_PRESET: None,
    i18n.SELECT_MIDI_FILE_DESCRIPTION: None,
    i18n.SELECT_THE_ACTION_TO_RENAME: None,
    i18n.SHOW_OTHER_TOOLS_PANEL: None,
    i18n.SHOW_OTHER_TOOLS_PANEL_IF_ENABLED: None,
    i18n.SINUSOIDAL: None,
    i18n.SKIP: None,
    i18n.SKIP_KEYFRAME_DESCRIPTION: None,
    i18n.SKIP_OVERLAPS: None,
    i18n.SOUND: None,
    i18n.SOUND_TO_ANIMATE: None,
    i18n.SPEAKER: None,
    i18n.SPEAKER_TO_ANIMATE: None,
    i18n.START: None,
    i18n.STARTING_NOTE: None,
    i18n.START_TIME: None,
    i18n.START_TIME_FILTER_DESCRIPTION: None,
    i18n.SUBTRACT: None,
    i18n.SYNC_LENGTH_WITH_NOTES: None,
    i18n.SYNC_LENGTH_WITH_NOTES_DESCRIPTION: None,
    i18n.TEMPERATURE: None,
    i18n.TEXT: None,
    i18n.TEXTURE: None,
    i18n.TEXTURE_TO_ANIMATE: None,
    i18n.TEXT_TO_ANIMATE: None,
    i18n.THE_ACTION_TO_RENAME: None,
    i18n.THE_NODE_TREE_TO_ANIMATE: None,
    i18n.TICKS_PER_BEAT: None,
    i18n.TIME_UNIT: None,
    i18n.TOOL: None,
    i18n.TRACK: None,
    i18n.TRANSITION_END_DESCRIPTION: None,
    i18n.TRANSITION_LENGTH_FRAMES: None,
    i18n.TRANSITION_LIMIT_FRAMES_DESCRIPTION: None,
    i18n.TRANSITION_OFFSET_FRAMES: None,
    i18n.TRANSITION_OFFSET_FRAMES_DESCRIPTION: None,
    i18n.TRANSITION_PLACEMENT: None,
    i18n.TRANSITION_START_DESCRIPTION: None,
    i18n.TRANSPOSE: None,
    i18n.TRANSPOSE_ALL: None,
    i18n.TRANSPOSE_ALL_FILTERS: None,
    i18n.TRANSPOSE_EXCEPT_ALL_INCLUSIVE: None,
    i18n.TRANSPOSE_EXCEPT_ALL_INCLUSIVE_DESCRIPTION: None,
    i18n.TRANSPOSE_FILTERS: None,
    i18n.TRANSPOSE_FILTERS_DESCRIPTION: None,
    i18n.TRANSPOSE_IF_POSSIBLE: None,
    i18n.TRANSPOSE_IF_POSSIBLE_DESCRIPTION: None,
    i18n.TRANSPOSE_IF_POSSIBLE_EXCEPT_ALL_DESCRIPTION: None,
    i18n.TRANSPOSE_IF_POSSIBLE_EXCEPT_ALL_INCLUSIVE: None,
    i18n.TRANSPOSE_INSTRUMENT: None,
    i18n.TRANSPOSE_INSTRUMENT_OP: None,
    i18n.TRANSPOSE_STEPS: None,
    i18n.TYPE: None,
    i18n.TYPE_DESCRIPTION: "Tipo de objeto para aplicar la acción",
    i18n.UNIT_TYPE: None,
    i18n.VELOCITY: None,
    i18n.VELOCITY_FILTER_DESCRIPTION: None,
    i18n.VOLUME: None,
    i18n.VOLUME_TO_ANIMATE: None,
    i18n.WORLD: None,
    i18n.WORLD_TO_ANIMATE: None
}
