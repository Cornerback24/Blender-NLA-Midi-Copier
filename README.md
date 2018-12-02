# Blender NLA Midi Copier
Blender add-on for syncing duplicated action strips in the NLA Editor to notes in a midi file
This add-on is being developed for Blender 2.80

This add-on adds a panel to the NLA Editor for duplicating action strips and syncing them up with notes in a midi file.
It allows for selecting a track in a midi file and a note from that track, and then duplicating all the selected action strips to sync up with all instances of the selected note.  For example, an action strip could be duplicated to line up with all of the C4 notes played by a piano.

### Panel controls:
* Choose midi file:
  * Select a midi file.
* Midi File:
  * Displays the selected midi file.
* Track:
  * Choose a track from the midi file.  (Tracks with no notes will not be shown.)
* Note:
  * Choose a note from the selected track.  (Only notes contained by the selected track will be shown.)
* Copy to Notes:
  * Click this button to duplicate all of the selected action strips and line up the duplicates with all instances of the selected note.
* First Frame:
  * The frame that the midi file starts on.
* Frame offset:
  * Offset in frames to use when copying the note (can be negative).  For example, if the frame offset is -5, then the duplicated action strips will be placed 5 frames before the instances of the selected note.
* Copy to New Track
  * Place duplicated actions on a new track.
* Delete Source Action
  * Delete the action strip that is being duplicated.
* Delete Source Track
  * Delete the NlaTrack containing the action strip that is being duplicated, only if it is empty.
* Linked Duplicate
  * Use linked duplicate when duplicating strips.

### Other notes:
* The duplicated strips will all be placed on the same NlaTrack if possible.  If there are overlaps, new tracks will be created containing the overlapping action strips.
* If a text filter is enabled, it is possible that the duplicated action strips will be placed on new tracks that won't  be immediately visible due to being filtered by the text filter.