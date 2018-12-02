if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
else:
    from . import midi_data
import bpy


class NLAMidiCopier(bpy.types.Operator):
    bl_idname = "ops.nla_midi_copier"
    bl_label = "Copy to Notes"
    bl_description = "Copy the selected NLA-Strip(s) to the selected note"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        self.frames_per_second = context.scene.render.fps
        self.copied_strips = []  # action strips that were copied
        self.temp_track = None  # temporary tracks made to duplicate action strips onto
        self.note_tracks = []  # tracks that contain the copied strips
        self.frame_offset = (context.scene.midi_frame_start - 1) + context.scene.midi_frame_offset
        self.source_strips_copied = 0  # number of source action strips that were copied (not number of final copies)
        self.animation_data_list = None

        # these filters currently cause some issues, so for now abort action if they are active
        if context.space_data.dopesheet.filter_text != "" and context.space_data.dopesheet.use_multi_word_filter:
            self.report({"WARNING"}, "Multi-word filtering not supported")
            return

        selected_strips = self.selected_strips()
        if len(selected_strips) == 0:
            self.report({"INFO"}, "No action strips selected")
            return
        notes = midi_data.get_selected_notes(context)

        for nla_strip in selected_strips:
            self.copy_nla_strip_to_notes(nla_strip, notes, context)

        if self.source_strips_copied == 0:
            self.report({"INFO"}, "No action strips selected")
            return

        # select copied strips
        bpy.ops.nla.select_all(action="DESELECT")
        # if context.scene.copy_to_new_track and context.scene.delete_source_action_strip:
        # bpy.ops.nla.select_all_toggle()
        for nla_strip in self.copied_strips:
            nla_strip.select = True

    def copy_nla_strip_to_notes(self, nla_strip, notes, context):
        # select the strip to copy
        NLAMidiCopier.select_single_strip(nla_strip)
        # select the track containing the strip to copy so that the added track is placed above it
        self.select_track_containing_strip(nla_strip)
        source_track = self.selected_tracks()[0]

        notes_track = self.add_track()
        if notes_track is None:
            return  # notes_track will be None if nla_strip is filtered
        self.source_strips_copied += 1

        filter_text = context.space_data.dopesheet.filter_text
        # disable text filter while copying to prevent issues with new tracks being filtered
        context.space_data.dopesheet.filter_text = ""

        self.select_single_track(notes_track)
        self.temp_track = self.add_track()

        self.note_tracks = [notes_track]
        # notes_track.name = self.note_track_name(context)
        if len(notes) > 0:
            self.copy_nla_strip_to_note(nla_strip, notes[0], False, notes_track, context)
        nla_strip_copy = NLAMidiCopier.selected_strip(self.note_tracks)
        for note in notes[1:]:
            self.copy_nla_strip_to_note(nla_strip_copy, note, True, notes_track, context)

        # delete the temporary track that was created for duplications
        self.select_single_track(self.temp_track)
        bpy.ops.nla.tracks_delete()

        # delete the original action strip if preference is set
        if context.scene.delete_source_action_strip:
            NLAMidiCopier.select_single_strip(nla_strip)
            bpy.ops.nla.delete()

        # clean up extra tracks created due to overlapping events
        # (move strips down so that there are minimal extra tracks)
        deleted_note_tracks = []
        for track in self.note_tracks[1 if context.scene.copy_to_new_track else 0:]:
            for nla_strip in track.strips:
                NLAMidiCopier.select_single_strip(nla_strip)
                bpy.ops.nla.move_down()
            if len(track.strips) == 0:
                self.select_single_track(track)
                deleted_note_tracks.append(track)
                bpy.ops.nla.tracks_delete()
        for deleted_track in deleted_note_tracks:
            self.note_tracks.remove(deleted_track)

        if context.scene.delete_source_track and len(source_track.strips) == 0:
            self.select_single_track(source_track)
            bpy.ops.nla.tracks_delete()

        # name the tracks containing the new action strips
        base_name = midi_data.get_note_id(context) + " - " + midi_data.get_track_id(context)
        extra_track_number = 0
        for track in self.note_tracks:
            if extra_track_number == 0:
                track.name = base_name
            else:
                track.name = base_name + " (" + str(extra_track_number) + ")"
            extra_track_number += 1

        # re-enable text filter if it was active
        context.space_data.dopesheet.filter_text = filter_text

    def copy_nla_strip_to_note(self, nla_strip, note, move_down, notes_track, context):
        NLAMidiCopier.select_single_strip(nla_strip)
        bpy.ops.nla.duplicate(linked=context.scene.midi_linked_duplicate_property)
        note_start_frame = (note.startTime / 1000) * self.frames_per_second
        move_distance_frames = int(note_start_frame - nla_strip.frame_start) + self.frame_offset
        bpy.ops.transform.translate(value=(move_distance_frames, 0, 0))
        if move_down:
            bpy.ops.nla.move_down()
            if len(self.temp_track.strips) > 0:
                self.note_tracks.append(self.temp_track)
                self.select_single_track(notes_track)
                self.temp_track = self.add_track()
        self.copied_strips.append(NLAMidiCopier.selected_strip(self.note_tracks))

    @staticmethod
    def select_single_strip(nla_strip):
        # deselect all
        bpy.ops.nla.select_all(action="DESELECT")
        nla_strip.select = True

    def select_single_track(self, nla_track):
        # deselect all
        for track in self.selected_tracks():
            track.select = False
        nla_track.select = True

    def selected_strips(self):
        selected_strips = \
            [
                strip for strip_list in
                [
                    track.strips for track in self.all_tracks()
                ]
                for strip in strip_list if strip.select
            ]

        return selected_strips

    def add_track(self):
        previous_selected_tracks = self.selected_tracks()
        bpy.ops.nla.tracks_add(above_selected=True)
        for track in self.selected_tracks():
            if track not in previous_selected_tracks:
                return track

    def select_track_containing_strip(self, nla_strip):
        for nla_track in self.all_tracks():
            nla_track.select = nla_strip in list(nla_track.strips)

    @staticmethod
    def selected_strip(nla_tracks):
        """
        :param nla_tracks: list of NlaTrack
        :return: the first selected NLA strip contained in the NLA Tracks
        """
        return next(
            nla_strip for nla_strip_list in
            [
                track.strips for track in nla_tracks
            ]
            for nla_strip in nla_strip_list if nla_strip.select
        )

    def selected_tracks(self):
        return \
            [
                track for track in self.all_tracks() if track.select
            ]

    def all_tracks(self):
        return \
            [
                track for track_list in
                [
                    animation_data.nla_tracks for animation_data in NLAMidiCopier.all_animation_data(self)
                ]
                for track in track_list
            ]

    def all_animation_data(self):
        if self.animation_data_list is None:
            self.animation_data_list = \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.armatures) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.cache_files) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.cameras) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.curves) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.grease_pencil) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.lights) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.lattices) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.linestyles) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.masks) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.materials) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.meshes) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.metaballs) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.movieclips) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.node_groups) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.objects) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.particles) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.scenes) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.shape_keys) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.speakers) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.textures) + \
                NLAMidiCopier.all_animation_data_from_collection(bpy.data.worlds)
        return self.animation_data_list

    @staticmethod
    def all_animation_data_from_collection(data_collection):
        return [x.animation_data for x in data_collection if x.animation_data is not None]
