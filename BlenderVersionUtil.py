from bpy.app import version as blender_version


def grease_pencil_object_type_string() -> str:
    return "GREASEPENCIL" if blender_version >= (4, 3, 0) else "GPENCIL"


def grease_pencil_action_id_type() -> str:
    """Action.id_root / ActionSlot.target_id_type for Grease Pencil data.

    4.2 actions use GREASEPENCIL. From 4.3 that identifier is legacy annotation
    data, and Grease Pencil v3 actions use GREASEPENCIL_V3.
    Object.type is a different enum: GPENCIL before 4.3, GREASEPENCIL after.
    """
    if blender_version >= (4, 3, 0):
        return "GREASEPENCIL_V3"
    return "GREASEPENCIL"


def grease_pencil_data_type():
    """RNA type for the Grease Pencil data-block the NLA copier animates.

    4.2: GreasePencil is the Grease Pencil ID. GreasePencilv3 exists in 4.2 but
    is not the data GPENCIL objects use.
    4.3–4.5: GreasePencil is legacy annotation data; v3 is GreasePencilv3.
    5.0+: GreasePencilv3 was renamed to GreasePencil. The id enum string
    stays GREASEPENCIL_V3.
    """
    import bpy
    if blender_version >= (4, 3, 0) and hasattr(bpy.types, "GreasePencilv3"):
        return bpy.types.GreasePencilv3
    return bpy.types.GreasePencil


def grease_pencil_frames_use_frame_numbers() -> bool:
    """Grease Pencil v3 frames.copy() and frames.remove() take frame numbers.

    Legacy GPencilFrames.copy() and remove() take the frame object. Both changed in 4.3.
    """
    return blender_version >= (4, 3, 0)


def has_slotted_actions() -> bool:
    return blender_version >= (4, 4, 0)
