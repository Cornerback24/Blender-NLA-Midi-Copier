if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PropertyUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from . import PropertyUtils
    from .i18n import i18n

from typing import List, Tuple


def add_to_collection(collection, default_name: str, id_property_source, id_property: str, update_new_object=None):
    """
    :param collection: collection to add to
    :param default_name: name of object to add
    :param id_property_source: parent property of id_property
    :param id_property: string collection property used to select by id
    :param update_new_object function to apply updates to the new object before it is set as selected
    :return added object
    """
    new_object = collection.add()
    new_object.name = i18n.concat(default_name, str(len(collection)))
    if update_new_object is not None:
        update_new_object(new_object)
    setattr(id_property_source, id_property, str(len(collection) - 1))
    return new_object


def remove_from_collection(collection, id_property_source, id_property: str):
    selected_id = getattr(id_property_source, id_property)
    if selected_id is not None and not selected_id == PropertyUtils.NO_SELECTION:
        object_index = int(selected_id)
        setattr(id_property_source, id_property, PropertyUtils.NO_SELECTION)
        collection.remove(object_index)


def populate_collection_id_enum_properties(enum_properties: List[Tuple[str, str, str, int]], collection_property,
                                           none_selected_description):
    """
    :param enum_properties: list to populate with enum properties
    :param collection_property: collection property to get ids from
    :param none_selected_description: description of enum used for none selected
    """
    enum_properties.clear()
    for i in range(len(collection_property)):
        obj = collection_property[i]
        # identifier is the index of the object in the collection property
        # explicitly define the number so that if a rename changes the position in the returned list,
        # the selected object is preserved
        enum_properties.append((str(i), obj.name, obj.name, i + 1))
    enum_properties.sort(key=lambda x: x[1].lower())
    enum_properties.insert(0, (PropertyUtils.NO_SELECTION, "", none_selected_description, 0))


def get_selected_object(selected_id, collection_property):
    if selected_id and not selected_id == PropertyUtils.NO_SELECTION:
        return collection_property[int(selected_id)]
    return None
