- 0.20.0 2025-1-7
  * Update to Blender extension 
- 0.19.1 2024-9-1
  * Fix tempo changes being applied at incorrect times
  * Fix loading midi files with relative paths
- 0.19.0 2024-4-13
  * Add All Pitches checkbox to filter groups
  * Update the Copy midi file data buttons to be available when midi file settings are different between the views  
  * Update CC Data in graph editor to always use selected pitch (unless there are pitch filters)
  * Fix single keyframe actions not generating a full frame length action strip when copied
- 0.18.0 2024-3-28
  * Add option to midi file selector for relative paths
  * Fixed parsing repeated notes when a Note On is listed before a Note Off at the same time
- 0.17.0 2023-7-14
  * Add filter presets
  * Add overlap filter
  * Fix add-on not remembering selected track and note when opening project
  * Hide internal use only properties on operators
  * Fix error coping grease pencil keyframes when sync length with notes is selected
- 0.16.1 2023-6-24
  * Fix graph editor pitch max value mapping
- 0.16.0 2023-6-11
  * Add keyframe generation from CC data to the graph editor
  * Replace graph editor keyframe placement dropdown with checkboxes
- 0.15.1 2022-11-23
  * Fix no room for action error when copying actions to a material's nodetree
- 0.15.0 2022-11-14
  * Add generate transitions tool to generate nonlinear transitions in the Nonlinear Animation view
  * Add delete transitions tool to delete transition strips in the Nonlinear Animation view
  * Add limit transition length option to Graph Editor keyframe generation
  * Add Note Start and End keyframe placement to Graph Editor keyframe generation
- 0.14.0 2022-10-27
  * Fix Sync Length with Notes repeating the action instead of scaling action length in Blender 3.3
  * Add repeat action option to Sync Length with notes
  * Add tool to rename actions from the Nonlinear Animation view
  * Disable Copy Action to Notes button if no action is selected
- 0.13.2 2022-9-21
  * Move user facing text to i18n (no functionality changes) 
  * Add Blender Addon Updater
- 0.13.1 2022-7-28
  * Update to use displayed track name for Copy by track and note name
  * Update to use displayed track name for generated nla track names
- 0.13.0 2022-7-28
  * Add ability to rename midi tracks to the midi settings panel 
  * Add Copy by track and note name option to quick copy tools
  * Add Copy to selected objects only option to quick copy tools
  * Fix compatibility with Blender 2.80
  * Fix error when copying grease pencil keyframes
  * Fix error caused by changing the selected note to an invalid pitch when transposing an instrument
- 0.12.1 2022-2-21
  * Add Particle to action types
  * Add icons to Type selection
  * Fix two actions being undone when undo is used after selecting a midi file 
- 0.12.0 2021-12-4
  * Add note length and note velocity based keyframe generation in the graph editor
  * Add skip note overlap option to the graph editor
  * Add note filters to the graph editor
  * Add note start time filter
  * Add tool to load midi file data from another view
  * Add tool in the graph editor to load min and max values from the selected midi track
  * Add Node Tree to Types (for geometry nodes)
  * Update graph editor keyframe generation to copy to all selected fcurves
  * Update Copy Action button tooltip when no midi file is selected
  * Update Copy Keyframes button in Grease Pencil view to be disabled when no midi file is selected
  * Replace Duplicate on Overlap checkbox with Overlap dropdown
  * Replace None Blending option with Overlap dropdown
- 0.11.0 2021-6-27
  * Change the name of the Copy Along Path and Copy to Instrument panel to Quick Copy Tools
  * Add tool to copy to notes based on object name
  * Update note search box to show note name instead if the note is changed and the search box was already showing a not name (instead of a note number)  
- 0.10.2 2021-3-20
  * Fix reloading script
- 0.10.1 2021-3-15
  * Fix loading add-on in Blender 2.90
- 0.10.0 2021-3-14
  * Add pitch-based keyframe generation in the graph editor
  * Add search boxes to note fields so notes can be selected by typing a note name or midi note number
  * Update the midi file selection dialog to filter by *.mid and *.midi files
  * Update note properties to be stored by midi note number (except for middle c properties)
- 0.9.3 2021-2-14
  * Add copy to selected and copy along path support for shape keys
- 0.9.2 2020-12-31
  * Add copy to selected and copy along path support for materials
- 0.9.1 2020-11-14
  * Fix no room for strip error that could occur when scaling actions  
- 0.9.0 2020-9-26
  * Add support for type 0 midi files (all notes in type 0 files will be put on one track)
  * Add ability to change tempo in midi settings panel
  * Add copy to note end to grease pencil keyframes
  * Fix accessing midi tracks when the display name is different from the file's track name
  * Fix tracks not being selectable when the track name is a null character (display name is changed in this case) 
- 0.8.1 2020-9-22
  * Fix parsing SequencerSpecificEvent
- 0.8.0 2020-8-31
  * Add copy along path option for quickly animating multiple objects to different notes if they all share the same action.
  * Fix overlaps being detected when nla strip is adjacent but not overlapping
  * Change scaling so that nla strip end times are always integer frames
- 0.7.3 2020-7-18
  * Add ability to copy to end of note
  * Fix issue where copying a scaled down action to a track with existing actions could result in a no room for strip error.                                                                                              
- 0.7.2 2020-7-11
  * Fix copying to instrument creating a blank filter group (revert automatically adding filter group)
- 0.7.1 2020-7-6
  * Add support for Duplicate on Overlap and Copy to Selected to more types.
  * Add support for Copy to selected to more types.
  * Add a "Selected" pitch filter to match selected note.
  * Add a filter group when "Add filters" is selected if there isn't already an existing filter group.
- 0.7.0 2020-7-6
  * Add copy to single track for instruments option (instead of one track per note).
  * Add blend type for overlapping nla strips on additional nla tracks. 
  * Add ability to copy actions from the midi panel to an instrument.
  * Add search box for instrument notes.
  * Add frame offset that affects an entire instrument (replaces default frame offset for instrument actions).
  * Update to copy to an existing track if the track name matches.
- 0.6.2 2020-6-13
  * Fix incompatibility with Blender 2.83 grease pencil. 
  * Fix frame number off by one when coping grease pencil frames.
- 0.6.1 2020-5-6
  * Add note length filter.
  * Add velocity filter.
- 0.6.0 2020-3-5
  * Add filters.
  * Add filter groups.
  * Add start time filter.
  * Add pitch filter.
  * Add alternation filter (copy every n notes starting with note m).
  * Add middle c display property (changes what octaves are displayed, such as C3 vs C4 vs C5 for midi note 60).
- 0.5.4 2020-2-23
  * GNU License (#2)
  * Update script meta info (add wiki url to readme, bug tracker url, community support category).
- 0.5.3 2019-8-5
  * Fix failure to parse midi files with running status channel events.
- 0.5.2 2019-7-24
  * Fix sync length with notes option being unavailable for non-object actions.
  * Fix possible issue with copy with duplication on overlap (actions may have been copied to the wrong duplicated object).
- 0.5.1 2019-7-21
  * Add a button to animate all instruments.
  * Fix coping node tree actions.
- 0.5.0 2019-7-20
  * Add an option to scale copied NLA strips to note length.
  * Add option to scale copied grease pencil frames to note length
- 0.4.0 2019-7-19
  * Add support for copying grease pencil frames.
- 0.3.2 2019-7-13
  * fix panel naming convention warnings
- 0.3.1 2019-4-14
  * Add support for actions defined on a material's node tree.
- 0.3.0 2018-2-16
  * Add instruments. An instrument is a collection of actions for each note.
- 0.2.0 2019-2-2
  * Update from duplicating nla strips to making new nla strips with a selected action.  
- 0.1.0 2018-12-1  
  * Update to Blender 2.80.

