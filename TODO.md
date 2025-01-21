URGENT: ctrl+end shortcut / fix all the shortcuts

HIGH: phase deserialize doesn't load correctly
HIGH: add periodic saving
HIGH: If its any sort of auto-evac problem, clean the bumper
HIGH: If the robot doesn't turn on at all or liquid damage, test the battery
HIGH: add a global shortcut to jump focus to input box
HIGH: in checking the user dock charging contacts, add the ability to include notes
HIGH: If there's a bad contact, still check the battery if I need to
HIGH: when doing a mobility test, if the dock specified is a base, not a dock, ask to confirm the bin does not have ad evac port, and if it should
HIGH: add ctrl+A to *all* input boxes
HIGH: J1-6 don't have DCT cards specified

MEDIUM: add mobility test step to debugging phase
MEDIUM: Add some toasts? (copied, pick up case, case ref copied, etc)
MEDIUM: ctrl+home/ctrl+end
MEDIUM: J955 - 1st 5 means evac dock, 1 means base. 2nd 5, if 7, means lapis bin
MEDIUM: Consider a "clear TODO" button (or at least make it select everything on focus)
MEDIUM:  make the DCT card a single line
MEDIUM: Add an indicator to the tabs when the case is finished
MEDIUM: in mobility mission menu and combo (not can_mop), ask if tank is full
MEDIUM: lose case from input box (may already work?)
MEDIUM: copy serial button gets pushed off page if window too small
MEDIUM: if replaced bot and dock, combine them in external notes
MEDIUM: set capitalization for each word in the Dock: box in the mobility menu
MEDIUM: if battery tests are needed, also measure contacts, even if they don't feel sunken, but allow na
MEDIUM: in checking the SPL SKU confirm phase step, parse the serial and give it (i.e. "Is the SPL SKU 577?")
MEDIUM: add a binary slider in mobility menu to manually control the overall result, but which gets self-updated
MEDIUM: if provisioned on app, remind in finish phase to factory reset again -- not sure how to tell
MEDIUM: if factory reset and factory reset and mop bin, combine the 2 automatically (in external notes)
MEDIUM: have a step in swap that asks for the new serial, so it can update the sidebar with it. BUT keep the old serial. Also in that step, auto copy
MEDIUM: in mobility menu, show what the customer states is, for reference
MEDIUM: in mobility menu, organize by how often i use it, not by sequence
MEDIUM: add a binding for recovering state from the state backup file
MEDIUM: in step "put bot and traveler on shelf", add "and box"
MEDIUM: in mobility menu, make the spray test disabled unless M6
MEDIUM: add "esc" binding to both menus
MEDIUM: add a "put on hold" phase
MEDIUM: have a variable that indicates a rusted bin screw, for the external notes menu
MEDIUM: if serial numbers are different, automatically go to a new step that offers (and allows) you to close the case immediately
MEDIUM: Auto-guess which test dock the mobility test will use
MEDUIM: if we measured one contact, and it's good, ask if the other one needs to be measured as well

LOW: clean chirp sensor holes, if needed
LOW: some sort of reminder to clean the bin sensors: especially if they come in with bin not clearing and/or evac issues
LOW: If swap, copy the robot's defective serial number
LOW: if it's a big base, and it's any sort of vacuum stall or filter clog or something, remind to check the dock evac channel
LOW: ctrl + backspace doesn't seem to work
LOW: on focus (window focus, at least), the input shouldn't select all of it's text
LOW: make it so it finds where it should put text, so lower down I can manually add notes and it won't keep just adding to the end
LOW: strip input box text
LOW: confirm closing a case
LOW: ctrl + t is toggle case
LOW: double click select word
LOW: warn if the robot has an evac bin and/or dock, and I haven't mobility tested with evac bin, or with customers dock
LOW: maybe have up and down keys put the previous lines in the input box to edit
LOW: remind to stick DCT cable under the mop pad in combo modles
LOW: include robot nicknames
LOW: add a binding to auto-compact large cases to fit within 4000 characters
LOW: Add some color to the notes area to make things easily distinguishable (but make sure not to copy it!)
LOW: add a "can close" variable to case
LOW: Bold the 3 middle characters of the ref id?
LOW: I can auto remove lines if there's 3 newlines in a row
LOW: maaaybe try to auto generate and send the swap email
LOW: back broke
LOW: only c9's can refill
LOW: add a warning or something if characters exceed 4000
LOW: Adding proper versioning is a good idea
LOW: in the mobility menu, have the outline reflect whether the ultimate result is a pass or fail (with red/green)
LOW: if no dock indicated on dock (in mobility menu), then auto-unselect dock and undock sliders
LOW: in add_step(): if the previous line has "** Result: " in it, add an extra line -- maybe
LOW: on double check, add "double checked by michelle" to the notes (and then recopy the notes into CSS)
LOW: Add a readme with run instructions and the like
LOW: if the text_area ends in "* ", remove it as well
LOW: ask about the blower motor after cleaning, not before
LOW: See if bot charges on customer dock BEFORE battery test (if both applicable)
LOW: If a bot needs a battery test, ask about it immediately before cleaning

TEST: dct exceptions
TEST: adding text manually
TEST: for changing color
TEST: adding 5 cases all at once
TEST: tests for combos vs non-combos
TEST: tests for seralizing/deserializing

EPIC: Consider an option to reopen a case
EPIC: autocorrect, somehow?
EPIC: At the end, do a bunch of regex on the notes and confirm that I'm not forgetting anything -- including adding in the customer notes that a
EPIC: add if the dock or bot have been swapped next to the TODO box for context, along with other context things (factory reset, etc)
EPIC: add a double check phase, after finish, that regexes everything. Include: factory reset, swap, dct
EPIC: combine step "clean dock" and "clean base" -- this will actually take a rewrite to enable dynamic steps
EPIC: make the serial and ref labels into a new class that is a "CopyText" or something like that: a button that when clicked gets copied

MINOR: change/check the shade of blue
MINOR: if "lapis" mentioned in the notes, OR if there's a 7 in the serial number place, remind to reprovision lapis bin in the app in the external

factory reset was performed
