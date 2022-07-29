if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from . import i18n

i18n_es = {
    i18n.CHOOSE_MIDI_FILE: "Elegir archivo midi",
    i18n.COPY_ACTION_TO_SELECTED_OBJECTS: "Copiar acción a objetos seleccionados",
    i18n.TYPE_DESCRIPTION: "Tipo de objeto para aplicar la acción"
}
