if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(OperatorUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(CollectionUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PropertyUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from . import NoteFilterImplementations
    from . import NoteFilterModule
    from . import OperatorUtils
    from . import CollectionUtils
    from . import PropertyUtils
    from . import midi_data
    from .i18n import i18n

import bpy
from .NoteFilterModule import ReorderFilter, RemoveNoteFilter, RemoveFilterGroup, AddNoteFilter, AddNoteFilterGroup, \
    AddFilterPreset, SaveFilterPreset, DeleteFilterPreset
from .midi_data import MidiDataType


class MidiFileSelector(bpy.types.Operator):
    bl_idname = "ops.nla_midi_file_selector"
    bl_label = i18n.get_key(i18n.CHOOSE_MIDI_FILE_OP)
    bl_description = i18n.get_key(i18n.SELECT_MIDI_FILE_DESCRIPTION)
    bl_options = {"REGISTER", "UNDO"}
    # noinspection PyArgumentList,PyUnresolvedReferences
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.mid;*.midi", options={'HIDDEN'})
    # blender handles getting the path based on this behind the scenes
    relative_path: bpy.props.BoolProperty(name=i18n.get_key(i18n.RELATIVE_PATH),
                                          description=i18n.get_key(i18n.USE_RELATIVE_PATH_TO_MIDI_FILE))
    midi_data_type: bpy.props.IntProperty(name="MidiDataType", options={'HIDDEN'})

    def execute(self, context):
        OperatorUtils.load_midi_file(self, context, self.midi_data_type, self.filepath)
        return {'FINISHED'}

    # noinspection PyUnusedLocal
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def draw_common_midi_settings(parent_layout, context, midi_data_type: int):
    midi_data_property = midi_data.get_midi_data_property(midi_data_type, context)
    col = parent_layout.column(align=True)
    col.prop(midi_data_property, "middle_c_note")
    col.separator()
    draw_tempo_settings(col, midi_data_property.tempo_settings)

    col.separator()
    col.label(text=i18n.get_label(i18n.MIDI_TRACKS))
    track_names_row = parent_layout.row()
    col = track_names_row.column(align=True)
    col.template_list("MIDI_TRACK_PROPERTIES_UL_list", "", midi_data_property,
                      "midi_track_properties",
                      midi_data_property, "midi_track_property_index")
    if len(midi_data_property.midi_track_properties) > 0 and \
            (0 <= midi_data_property.midi_track_property_index < len(midi_data_property.midi_track_properties)):
        selected = midi_data_property.midi_track_properties[midi_data_property.midi_track_property_index]
        col.prop(selected, "displayed_track_name")


def draw_expand_handle(parent: bpy.types.UILayout, text: str, object_with_expand_property, expand_property_field: str):
    """
    :param parent: the parent layout
    :param text: the text for the expand handle
    :param object_with_expand_property: object with the expand/collapse property
    :param expand_property_field: expand/collapse field on the object
    :return: None
    """
    parent.prop(object_with_expand_property, expand_property_field, text=text,
                icon="TRIA_DOWN" if getattr(object_with_expand_property, expand_property_field) else "TRIA_RIGHT",
                icon_only=True, emboss=False)


def draw_collapsible_box(parent: bpy.types.UILayout, text: str, object_with_expand_property,
                         expand_property_field: str, remove_operator_id: str = None):
    """
    :param parent: the parent layout
    :param text: the text for the expand handle
    :param object_with_expand_property: object with the expand/collapse property
    :param expand_property_field: expand/collapse field on the object
    :param remove_operator_id: id of the remove operator (may be None for no remove operator)
    :return: (the collapsible box, remove operator)
    """
    box = parent.box()
    row = box.row()
    draw_expand_handle(row, text, object_with_expand_property, expand_property_field)
    if remove_operator_id is not None:
        remove_operator = row.operator(remove_operator_id, icon='CANCEL', text='')
    else:
        remove_operator = None

    return box, remove_operator


def set_operator_lookup_properties(operator, midi_data_type, is_part_of_instrument, action_index=None,
                                   filter_group_index=None, filter_index=None):
    """
    Set properties on an operator that the operator uses to look up data
    :param operator: the operator
    :param midi_data_type: midi data type
    :param is_part_of_instrument: True if data is part of an instrument
    :param action_index: action index used if data is part of an instrument
    :param filter_group_index: filter group index
    :param filter_index: filter index
    """
    operator.midi_data_type = midi_data_type
    operator.is_part_of_instrument = is_part_of_instrument
    if is_part_of_instrument:
        operator.action_index = action_index
    if filter_group_index is not None:
        operator.filter_group_index = filter_group_index
    if filter_index is not None:
        operator.filter_index = filter_index


def draw_filter_box(parent_layout, note_action_property, is_instrument_property, action_index, midi_data_type, context,
                    draw_all_pitches_checkbox: bool = True):
    box = draw_collapsible_box(parent_layout, i18n.get_key(i18n.FILTERS), note_action_property, "filters_expanded")[0]
    if note_action_property.filters_expanded:
        filter_group_index = 0
        for filter_group in note_action_property.note_filter_groups:
            draw_filter_group(box, filter_group, is_instrument_property, action_index, filter_group_index,
                              midi_data_type, draw_all_pitches_checkbox)
            filter_group_index += 1

        col = box.column(align=True)
        add_filter_group_operator = col.operator(AddNoteFilterGroup.bl_idname)
        set_operator_lookup_properties(add_filter_group_operator, midi_data_type, is_instrument_property, action_index)

    presets_box = draw_collapsible_box(box, i18n.get_key(i18n.FILTER_PRESETS),
                                       note_action_property, "filter_presets_box_expanded")[0]
    if note_action_property.filter_presets_box_expanded:
        row = presets_box.row()
        row.prop(note_action_property, "selected_note_filter_preset")
        add_preset_operator = row.operator(AddFilterPreset.bl_idname)
        set_operator_lookup_properties(add_preset_operator, midi_data_type, is_instrument_property, action_index)
        selected_filter_preset = CollectionUtils.get_selected_object(
            note_action_property.selected_note_filter_preset,
            context.scene.midi_copier_data_common.filter_presets)
        if selected_filter_preset is not None:
            row = presets_box.row()
            row.prop(selected_filter_preset, "name")
            preset_equals_current_filter = PropertyUtils.compare_filters(
                selected_filter_preset.note_filter_groups,
                note_action_property.note_filter_groups)
            save_operator_text = i18n.get_key(i18n.SAVE)
            if not preset_equals_current_filter:
                save_operator_text = "* " + save_operator_text
            save_preset_operator = row.operator(SaveFilterPreset.bl_idname, text=save_operator_text)
            set_operator_lookup_properties(save_preset_operator, midi_data_type, is_instrument_property, action_index)
            delete_preset_operator = row.operator(DeleteFilterPreset.bl_idname)
            set_operator_lookup_properties(delete_preset_operator, midi_data_type, is_instrument_property, action_index)


def draw_filter_group(parent_layout, filter_group_property, is_instrument_property, action_index,
                      filter_group_index, midi_data_type, draw_all_pitches_checkbox: bool):
    collapsible_box = draw_collapsible_box(
        parent_layout, i18n.concat(i18n.get_text(i18n.FILTER_GROUP), str(filter_group_index + 1)),
        filter_group_property, "expanded", RemoveFilterGroup.bl_idname)
    box = collapsible_box[0]
    remove_operator = collapsible_box[1]
    set_operator_lookup_properties(remove_operator, midi_data_type, is_instrument_property, action_index,
                                   filter_group_index)

    if filter_group_property.expanded:
        draw_filters_list(action_index, box, filter_group_index, filter_group_property, is_instrument_property,
                          midi_data_type, draw_all_pitches_checkbox)


def draw_filters_list(action_index, box, filter_group_index, filter_group_property, is_instrument_property,
                      midi_data_type, draw_all_pitches_checkbox: bool):
    filter_index = 0
    filter_count = len(filter_group_property.note_filters)
    all_pitches_row = box.row() if draw_all_pitches_checkbox else None
    pitch_filter_exists = False
    for filter_property in filter_group_property.note_filters:
        draw_filter(box, filter_property, is_instrument_property, action_index, filter_group_index,
                    filter_index, filter_count, midi_data_type)
        filter_index = filter_index + 1
        if filter_property.filter_type == NoteFilterImplementations.PitchFilter.ID:
            pitch_filter_exists = True
    # draw the All Pitches checkbox above the filters
    if draw_all_pitches_checkbox:
        all_pitches_row.enabled = not pitch_filter_exists
        all_pitches_row.prop(filter_group_property,
                             "all_pitches_selected_read_only" if pitch_filter_exists else "all_pitches")
    final_row = box.row()
    add_filter_operator = final_row.operator(AddNoteFilter.bl_idname, text=i18n.get_key(i18n.ADD_FILTER_OP))
    set_operator_lookup_properties(add_filter_operator, midi_data_type, is_instrument_property, action_index,
                                   filter_group_index)


def draw_filter(parent_layout, filter_property, is_instrument_property, action_index, filter_group_index,
                filter_index, filter_count, midi_data_type):
    filter_class = NoteFilterImplementations.ID_TO_FILTER[filter_property.filter_type]

    filter_row_container = parent_layout.row().split(factor=filter_class.NAME_DISPLAY_WEIGHT)
    left, filter_row = (filter_row_container.row(), filter_row_container.row())
    left.prop(filter_property, "filter_type", text="")
    filter_class.draw_ui(filter_row, filter_property)

    if filter_index > 0:
        move_up_operator = filter_row.operator(ReorderFilter.bl_idname, text='', icon='SORT_DESC')
        set_operator_lookup_properties(move_up_operator, midi_data_type, is_instrument_property, action_index,
                                       filter_group_index, filter_index)
        move_up_operator.reorder_factor = -1

    if filter_index + 1 < filter_count:
        move_down_operator = filter_row.operator(ReorderFilter.bl_idname, text='', icon='SORT_ASC')
        set_operator_lookup_properties(move_down_operator, midi_data_type, is_instrument_property, action_index,
                                       filter_group_index, filter_index)
        move_down_operator.reorder_factor = 1

    remove_filter_operator = filter_row.operator(RemoveNoteFilter.bl_idname, text='', icon='CANCEL')
    set_operator_lookup_properties(remove_filter_operator, midi_data_type, is_instrument_property, action_index,
                                   filter_group_index, filter_index)


def indented_row(parent_layout):
    split = parent_layout.row().split(factor=0.05)
    split1, row = split.row(), split.row()
    return row


def split_row(parent_layout, factor):
    """
    :param parent_layout: layout to place row in
    :param factor: spilt factor
    :return: (left row, right row, split row)
    """
    split = parent_layout.row().split(factor=factor)
    return split.row(), split.row(), split


def draw_note_with_search(parent_layout, parent_property, note_property: str, search_property: str, enabled=True,
                          text=None):
    """

    :param parent_layout: layout to drawn row on
    :param parent_property: property containing the note property
    :param note_property: note property
    :param search_property: note search string property
    :param enabled: if the row should be enabled
    :param text: Text for label. Supplying a label changes the alignment to align with properties
     drawn with draw_property_on_split_row
    """
    if text is None:
        left, right, note_row = split_row(parent_layout, .80)
        left.prop(parent_property, note_property)
        right.prop(parent_property, search_property, text="")
        note_row.enabled = enabled
    else:
        draw_property_on_split_row(parent_layout, parent_property, text, note_property, search_property)


def draw_tempo_settings(parent_layout, tempo_property):
    bpm_row = parent_layout.row()
    bpm_row.prop(tempo_property, "use_file_tempo")
    if not tempo_property.use_file_tempo:
        bpm_row.prop(tempo_property, "beats_per_minute")
    else:
        bpm_row.prop(tempo_property, "file_beats_per_minute")

    ticks_per_beat_row = parent_layout.row()
    ticks_per_beat_row.enabled = not tempo_property.use_file_tempo
    ticks_per_beat_row.prop(tempo_property, "use_file_ticks_per_beat")
    if not tempo_property.use_file_ticks_per_beat:
        ticks_per_beat_row.prop(tempo_property, "ticks_per_beat")
    else:
        ticks_per_beat_row.prop(tempo_property, "file_ticks_per_beat")


COPY_MIDI_FILE_DICTIONARY = {MidiDataType.NLA: ("NLA", i18n.get_key(i18n.COPY_FILE_FROM_NLA_DESCRIPTION)),
                             MidiDataType.DOPESHEET: (
                                 "GREASEPENCIL", i18n.get_key(i18n.COPY_FILE_FROM_DOPESHEET_DESCRIPTION)),
                             MidiDataType.GRAPH_EDITOR: (
                                 "GRAPH", i18n.get_key(i18n.COPY_FILE_FROM_GRAPH_EDITOR_DESCRIPTION))}


def draw_midi_file_selections(parent_layout, midi_data_property, midi_data_type: int, context,
                              note_property_text=i18n.get_label(i18n.NOTE)):
    def draw_copy_to_operator(copy_to_parent_layout, data_type_from, data_type_to):
        copy_from_midi_file = midi_data.get_midi_data_property(data_type_from, context).midi_file
        if copy_from_midi_file is not None and len(copy_from_midi_file) > 0:
            icon = COPY_MIDI_FILE_DICTIONARY[data_type_from][0]
            tooltip = i18n.get_text_tip(COPY_MIDI_FILE_DICTIONARY[data_type_from][1])
            copy_to_operator = copy_to_parent_layout.operator(OperatorUtils.CopyMidiFileData.bl_idname, text="",
                                                              icon=icon)
            copy_to_operator.copy_from_data_type = data_type_from
            copy_to_operator.copy_to_data_type = data_type_to
            copy_to_operator.tooltip = tooltip

    load_file_row = parent_layout.row()
    file_selector_operator = load_file_row.operator(MidiFileSelector.bl_idname,
                                                    icon='FILE_FOLDER')
    file_selector_operator.midi_data_type = midi_data_type

    # draw options to copy midi file data from other views
    for data_type in midi_data.MidiDataType.values():
        if data_type != midi_data_property.data_type and not (
                OperatorUtils.CopyMidiFileData.compare_midi_file_data(context, data_type,
                                                                      midi_data_property.data_type)):
            draw_copy_to_operator(load_file_row, data_type, midi_data_property.data_type)

    if midi_data_property.midi_file:
        draw_property_on_split_row(parent_layout, midi_data_property, i18n.get_label(i18n.MIDI_FILE), "midi_file")
        draw_property_on_split_row(parent_layout, midi_data_property, i18n.get_label(i18n.TRACK), "track_list")
        draw_property_on_split_row(parent_layout, midi_data_property, note_property_text, "notes_list",
                                   "note_search_string")


def draw_property_on_split_row(parent_layout, data, label, prop, second_prop=None, split_factor=0.2,
                               second_property_split_factor=0.7):
    """
    UILayout.prop() draws [label: property]. It doesn't visually line up in a list if using a split row to draw
    [label: property property]. This method can be used to draw both [label: property] and [label: property property]
    with both visually aligning in the ui.

    :param parent_layout: layout to place the row on
    :param label: the label for the property
    :param data: data for UILayout.prop()
    :param prop: property for UILayout.prop()
    :param second_prop: second property to place on the row (optional)
    :param split_factor: factor for UILayout.split() between label and property
    :param second_property_split_factor: factor for UILayout.split() if drawing two properties on the row
    :return:
    """
    left, right, row = split_row(parent_layout, split_factor)
    left.label(text=label)
    if second_prop is not None:
        left, right, row = split_row(right, second_property_split_factor)
        left.prop(data, prop, text="")
        right.prop(data, second_prop, text="")
    else:
        right.prop(data, prop, text="")


def draw_scale_filter(parent_layout, data, filter_type_property: str, scale_property: str):
    parent_layout.prop(data, filter_type_property)
    scale_row = indented_row(parent_layout)
    scale_row.enabled = not getattr(data, filter_type_property) == "no_filter"
    scale_row.prop(data, scale_property)


class OperatorTooltipCreator:
    """
    Handles creating a tooltip for an operator with information on why the operator is disabled
    (or just the operator description if it not disabled)
    """

    def __init__(self, operator_class, base_tooltip=None, button_text=None):
        """
        :param operator_class: blender Operator
        :param base_tooltip: base tooltip, operator description will be used if this is None
        :param button_text: text for the operator button. If None, uses the operator label
        """
        self.operator_class = operator_class
        self.base_tooltip = base_tooltip if base_tooltip is not None else i18n.get_text(operator_class.bl_description)
        self.disable_info = []  # list of reasons why the operator is disabled
        self.button_text = button_text

    def get_tooltip(self):
        tooltip = self.base_tooltip
        for disable_description in self.disable_info[:-1]:
            tooltip += (".\n  ! " + disable_description + ".")
        if len(self.disable_info) > 0:
            tooltip += (".\n  ! " + self.disable_info[-1])
        return tooltip

    def add_disable_description(self, disable_description: str):
        self.disable_info.append(disable_description)

    def is_disabled(self):
        return len(self.disable_info) > 0

    def draw_operator_row(self, parent_layout, icon="NONE"):
        """
        :param parent_layout: parent layout to place the operator on
        :param icon: icon for the operator
        :return: A row containing the operator. The row will be disabled if the tooltip create has any disable info.
        """
        operator_row = parent_layout.row()
        operator_row.enabled = not self.is_disabled()
        if self.button_text is None:
            operator = operator_row.operator(self.operator_class.bl_idname, icon=icon)
        else:
            operator = operator_row.operator(self.operator_class.bl_idname, text=self.button_text, icon=icon)
        operator.tooltip = self.get_tooltip()
