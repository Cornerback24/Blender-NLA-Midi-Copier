# Blender NLA Midi Copier
Blender add-on for creating midi-driven animations from the Nonlinear Animation view.  Adds a panel to the Nonlinear Animation view that allows for copying an action to each instance of a note in a midi file. For example, actions strips for a selected action could be generated to line up with all of the C4 notes played by a piano. To access the panel, expand the right-side panel in the Nonlinear Action View and select the Midi tab.
This add-on is being developed for Blender 2.80

### Panel controls:
* Choose midi file:
  * Select a midi file.
* Midi File:
  * Displays the selected midi file.
* Track:
  * Choose a track from the midi file. (Tracks with no notes will not be shown.)
* Note:
  * Choose a note from the selected track. (Only notes played in the selected track will be shown.)
* Type:
  * The type of object to animate. Select "Object" to animate objects in the scene. Change this value to animate something other than an object.  For example, select "Light" to animate the brightness of a light.
* Object:
  * The object to animate.  This field will change depending on the value of Type.  If Type is Object, this field will allow selecting an object, if Type is Light, this field will allow selecting a Light, ect.  
* Action:
  * The action to generate NLA Strips from. Only actions valid for the selected Type will be shown.
* Copy Action to Selected Objects:
  * If this option is selected, then the selected objects will be animated instead of the Object in the Object control. This option is only valid for Type Object. 
* Duplicate Object on Overlap:
  * If this option is selected, then overlapping action strips will be placed on new objects that are duplicates of the original object being animated.  If this option is not selected, then overlapping action strips will be omitted. This option is only valid for Type Object.
* Nla Track:
  * The name of the NLA track to place action strips on.  Action strips will be placed on a new track created with this name.  A name wil be automatically generated if this field is blank. 
* First Frame:
  * The frame that the midi file starts on.
* Frame Offset:
  * Offset in frames to use when generating action strips (can be negative). For example, if the frame offset is -5, then the generated action strips will be placed starting 5 frames before the instances of the selected note.
* Action Length (Frames):
  * The length of the action. Used to determine if the action overlaps another generation action. Defaults to the true length of the action. As an example, if this is set to 50 frames, and two notes are only 30 frames apart, then the action for the second note will be considered to overlap the action for the first note.  The second note's action will either be omitted or copied to a duplicate object, depending on whether Duplicate Object on Overlap is selected. If this value is set to less than the true length of the action, it will be replaced by the true length of the action. This control is not available if no action is selected.
* Copy Action to Notes:
  * Click this button to generate action scripts from the selected action that line up with all instances of the selected note.


### Installation:
* Installation is the normal installation process for multi-file add-ons.
  * Option 1: Download as a zip file. In Blender, go to Edit > Preferences > Add-ons, and click Install.  Select the zip file and click Install Add-on from File.
  * Option 2: Clone into the 2.80/scripts/addons directory in the Blender installation.
* To enable the add-on, in Blender, go to Edit > Preferences > Add-ons, and select Animation in the drop-down. Check the box next to the add-on to enable it.