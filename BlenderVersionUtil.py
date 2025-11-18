from bpy.app import version as blender_version


def grease_pencil_object_type_string() -> str:
    return "GREASEPENCIL" if blender_version >= (4, 3, 0) else "GPENCIL"


def grease_pencil_copy_accepts_frame_number() -> bool:
    return blender_version >= (4, 3, 0)


def has_slotted_actions() -> bool:
    return blender_version >= (4, 4, 0)
