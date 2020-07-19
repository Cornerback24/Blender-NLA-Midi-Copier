- 0.7.3 2020-7-18
  * Add ability to copy to end of note
  * Fix issue where copying a scaled down action to a track with existing actions could result in a no room for strip error                                                                                              
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

