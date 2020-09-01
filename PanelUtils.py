if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterModule)
else:
    # noinspection PyUnresolvedReferences
    from . import NoteFilterImplementations
    # noinspection PyUnresolvedReferences
    from . import NoteFilterModule

import bpy
from .NoteFilterModule import ReorderFilter, RemoveNoteFilter, RemoveFilterGroup, AddNoteFilter, AddNoteFilterGroup


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


def draw_filter_box(parent_layout, note_action_property, is_instrument_property, action_index, midi_data_accessor):
    box = draw_collapsible_box(parent_layout, "Filters", note_action_property, "filters_expanded")[0]
    if note_action_property.filters_expanded:
        filter_group_index = 0
        for filter_group in note_action_property.note_filter_groups:
            draw_filter_group(box, filter_group, is_instrument_property, action_index, filter_group_index,
                              midi_data_accessor)
            filter_group_index += 1

        col = box.column(align=True)
        add_filter_group_operator = col.operator(AddNoteFilterGroup.bl_idname)
        add_filter_group_operator.is_part_of_instrument = is_instrument_property
        add_filter_group_operator.midi_data_accessor = midi_data_accessor
        if is_instrument_property:
            add_filter_group_operator.action_index = action_index


def draw_filter_group(parent_layout, filter_group_property, is_instrument_property, action_index,
                      filter_group_index, midi_data_accessor):
    collapsible_box = draw_collapsible_box(
        parent_layout, "Filter Group " + str(filter_group_index + 1), filter_group_property,
        "expanded", RemoveFilterGroup.bl_idname)
    box = collapsible_box[0]
    remove_operator = collapsible_box[1]
    remove_operator.is_part_of_instrument = is_instrument_property
    remove_operator.midi_data_accessor = midi_data_accessor
    if is_instrument_property:
        remove_operator.action_index = action_index
    remove_operator.filter_group_index = filter_group_index

    if filter_group_property.expanded:
        draw_filters_list(action_index, box, filter_group_index, filter_group_property, is_instrument_property,
                          midi_data_accessor)


def draw_filters_list(action_index, box, filter_group_index, filter_group_property, is_instrument_property,
                      midi_data_accessor):
    filter_index = 0
    filter_count = len(filter_group_property.note_filters)
    for filter_property in filter_group_property.note_filters:
        draw_filter(box, filter_property, is_instrument_property, action_index, filter_group_index,
                    filter_index, filter_count, midi_data_accessor)
        filter_index = filter_index + 1
    final_row = box.row()
    add_filter_operator = final_row.operator(AddNoteFilter.bl_idname, text='Add filter')
    add_filter_operator.is_part_of_instrument = is_instrument_property
    add_filter_operator.midi_data_accessor = midi_data_accessor
    if is_instrument_property:
        add_filter_operator.action_index = action_index
    add_filter_operator.filter_group_index = filter_group_index


def draw_filter(parent_layout, filter_property, is_instrument_property, action_index, filter_group_index,
                filter_index, filter_count, midi_data_accessor):
    filter_class = NoteFilterImplementations.ID_TO_FILTER[filter_property.filter_type]

    filter_row_container = parent_layout.row().split(factor=filter_class.NAME_DISPLAY_WEIGHT)
    left, filter_row = (filter_row_container.row(), filter_row_container.row())
    left.prop(filter_property, "filter_type", text="")
    filter_class.draw_ui(filter_row, filter_property)

    if filter_index > 0:
        move_up_operator = filter_row.operator(ReorderFilter.bl_idname, text='', icon='SORT_DESC')
        move_up_operator.is_part_of_instrument = is_instrument_property
        move_up_operator.midi_data_accessor = midi_data_accessor
        if is_instrument_property:
            move_up_operator.action_index = action_index
        move_up_operator.filter_group_index = filter_group_index
        move_up_operator.filter_index = filter_index
        move_up_operator.reorder_factor = -1

    if filter_index + 1 < filter_count:
        move_down_operator = filter_row.operator(ReorderFilter.bl_idname, text='', icon='SORT_ASC')
        move_down_operator.is_part_of_instrument = is_instrument_property
        move_down_operator.midi_data_accessor = midi_data_accessor
        if is_instrument_property:
            move_down_operator.action_index = action_index
        move_down_operator.filter_group_index = filter_group_index
        move_down_operator.filter_index = filter_index
        move_down_operator.reorder_factor = 1

    remove_filter_operator = filter_row.operator(RemoveNoteFilter.bl_idname, text='', icon='CANCEL')
    remove_filter_operator.is_part_of_instrument = is_instrument_property
    remove_filter_operator.midi_data_accessor = midi_data_accessor
    if is_instrument_property:
        remove_filter_operator.action_index = action_index
    remove_filter_operator.filter_group_index = filter_group_index
    remove_filter_operator.filter_index = filter_index


def indented_row(parent_layout):
    split = parent_layout.row().split(factor=0.05)
    split1, row = split.row(), split.row()
    return row
