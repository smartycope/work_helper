URGENT: S9: no dock indicated, and still asking if there's a bag in the dock

MINOR: if mobility menu attempted to open with no cases, it throws an error. Catch that
MINOR: only if "lapis" mentioned in the notes, remind to reprovision lapis bin in the app in the external
MINOR: immediately after opening a new case, autofocus on the input box
MINOR: the colors of the CopyText buttons are arbitrary: make the text color the color of the case
MINOR: when checking for 'charg' or 'batt', also check for "does not turn on", or "doesn't turn on", or "won't turn on" and similar
MINOR: make the mobility todo box an input box and give it a placeholder
MINOR: in the comment in the texts.py that the steps have to be unique: they technically only have to be unique within each phase
MINOR: maybe - in the mobility menu update function, in the if statement to reset the dock box, remove the or'ed statement if it's empty (don't reset if it's empty)

HIGH: ctrl+end shortcut / fix all the shortcuts
HIGH: focus on input box on MM close
HIGH: give external notes menu open/close/toggle - or just make a Menu parent class
HIGH: when checking dock values, search the string instead of using == (alex-albany should still match Albany)
HIGH: in step " Found signs of liquid corrosion on the top board", if input is a single character, just assume motherboard
HIGH: add a step in swap phase to put a tag on the new bot
HIGH: on start of the program, load the currently saved state file
HIGH: regex for extracting the dock from notes also captures the comma and space before it
HIGH: mobility menu dock still using customer instead of cx (when using scraped dock info)
HIGH: on close of mobility menu, focus the end of the notes
HIGH: add a 2nd CopyText button for the other swap id, if there is one
HIGH: somehow emphasize C9's remove battery before CHM in notes
HIGH: cx stated charging error, and there was liquid damage, and did not ask for a battery test
HIGH: add a hotkey for ordering parts as follows: enter, tab x3, "NA", tab, "NA", tab x2, enter
HIGH: C9, Aurora, didn't ask to empty dock tank (I think, double check)
HIGH: auto guess the "where" in the mobility menu
HIGH: add a step (and make it the first step) in Finish phase, that asks if I've completed a successful mobility test, and attempted DCT
HIGH: when external notes menu opens via steps, it doesn't auto-load (call the open/toggle function instead of setting visible to True)
HIGH: add if the case has a lapis bin to notes -- and also that, if there's a lapis bin due to serial number, it doesn't need to be provisioned to the app to work
HIGH: in M6 bot, with no dock specified, it's asking if there's a bag in the dock - same case is asking if blower play
HIGH: if the case has a lapis bin, *in the serial number*, it should *not* suggest in external notes to reprovision bot to the lapis bin (and should even prevent it if it is checked, just disable it). But if the bot does *not* have a 7 in the serial, but *does* have one in the notes, (add a regex for it), then it *should* recommend reprovisioning, if a factory reset OR a swap
HIGH: phase deserialize doesn't load correctly
HIGH: add periodic saving
HIGH: add a global shortcut to jump focus to input box
HIGH: in checking the user dock charging contacts, add the ability to include notes
HIGH: when doing a mobility test, if the dock specified is a base, not a dock, ask to confirm the bin does not have ad evac port, and if it should
HIGH: add ctrl+A to *all* input boxes
HIGH: J1-6 don't have DCT cards specified

MEDIUM: Make "is there liquid damage" step allow for explanations, or just 'y' if simply "yes". Also, update the text to reflect this
MEDIUM: remove todo box can focus
MEDIUM: Auto-guess which test dock the mobility test will use
MEDIUM: add another hotkey sequence for add attachment:
down, enter, tab, enter, (shift+tab, shift+tab, down, up, enter) OR (type current id, down, enter), tab, "Repair Report", tab, enter
MEDIUM: in external notes menu, disallow "factory reset" and "replaced robot" to both be active at the same time
MEDIUM: improve the external notes swap regex (i.e. match swap, if not followed by dock or battery)
MEDUIM: add a step in final phase, if there was a swap, to salvage parts (consider adding it to an existing step)
MEDIUM: add a "put on hold" phase
MEDIUM: Add some toasts? (copied, pick up case, case ref copied, etc)
MEDIUM: ctrl+home/ctrl+end
MEDIUM: in the external notes regex, allow "swap dock", "swapped dock" and "swapping dock" (or robot)
MEDIUM: have copy be a custom function that, when called, cancels multi_paste()
MEDIUM: if mobility menu was opened automatically via step, and then closed via it's button, it should progress to the next step
MEDIUM: in "order correctly colored swap" (for M6 specifically) copy the serial (in step prior)
MEDIUM: add a "has been swapped" member that indicates whether the "order swap" step has been performed before, for the external notes menu to use
MEDIUM: put all the mobility menu switches for combos and mops on one side
MEDIUM: multi_paste() is buggy somehow, it stopped working after a while
MEDIUM: allow different serial numbers, if it follows the document (i.e. i5g5 instead of i5g7) (also, in the case of g, it means it's a lapis combo)
MEDIUM: J955 - 1st 5 means evac dock, 1 means base. 2nd 5, if 7, means lapis bin
MEDIUM: Consider a "clear TODO" button (or at least make it select everything on focus)
MEDIUM:  make the DCT card a single line
MEDIUM: Add an indicator to the tabs when the case is finished
MEDIUM: in mobility mission menu and combo (not can_mop), ask if tank is full
MEDIUM: lose case from input box (may already work?)
MEDIUM: copy serial button gets pushed off page if window too small
MEDIUM: if replaced bot and dock, combine them in external notes
MEDIUM: set capitalization for each word in the Dock: box in the mobility menu
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
MEDIUM: have a variable that indicates a rusted bin screw, for the external notes menu
MEDIUM: if serial numbers are different, automatically go to a new step that offers (and allows) you to close the case immediately
MEDIUM: if battery tests are needed, also measure contacts, even if they don't feel sunken, but allow na

LOW: add mobility test step to debugging phase
LOW: clean chirp sensor holes, if needed
LOW: some sort of reminder to clean the bin sensors: especially if they come in with bin not clearing and/or evac issues
LOW: If swap, copy the robot's defective serial number
LOW: if it's a big base, and it's any sort of vacuum stall or filter clog or something, remind to check the dock evac channel
LOW: ctrl + backspace doesn't seem to work
LOW: on focus (window focus, at least), the input shouldn't select all of it's text
LOW: make it so it finds where it should put text, so lower down I can manually add notes and it won't keep just adding to the end
LOW: add a switch to mobility menu to indicate testing a swapped bot
LOW: instead of manually uppercasing strings, turn it into a function, and don't un-uppercase the string if the 2nd letter is uppercase (we don't want "cHM is...")
LOW: consider refactoring all the private members into public properties, that return self._member or regex to find it if self._member is None
LOW: disallow unfocusing new case input box when visible
LOW: don't ask about sunken contacts on an S9 specifically
LOW: strip all input box text
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
LOW: If its any sort of auto-evac problem, clean the bumper
LOW: only c9's can refill
LOW: add a warning or something if characters exceed 4000
LOW: make all characters after 4000 be tinged red in notes
LOW: Adding proper versioning is a good idea
LOW: in the mobility menu, have the outline reflect whether the ultimate result is a pass or fail (with red/green)
LOW: if no dock indicated on dock (in mobility menu), then auto-unselect dock and undock sliders
LOW: in add_step(): if the previous line has "** Result: " in it, add an extra line -- maybe
LOW: on double check, add "double checked by michelle" to the notes (and then recopy the notes into CSS)
LOW: Add a readme with run instructions and the like
LOW: if the text_area ends in "* ", remove it as well
LOW: See if bot charges on customer dock BEFORE battery test (if both applicable)
LOW: If a bot needs a battery test, ask about it immediately before cleaning
LOW: change/check the shade of blue

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

EPIC: common phrases:
Attempting Aurora refill debug steps
Robot charges on <dock> @ ~nW
Battery test: n%/n%
Swapping bot
Swapping dock

EPIC: Put on hold phase:
copy notes over step
retrun any *unused* parts

EPIC: add specific "sections" (probably just more phases, maybe something distinct) for troubleshooting specific problems:
- Evac issues:
try cleaning the IR sensor
try swapping the CHM
check for a clog
try a new bin
try a new filter

EPIC: consider adding a bunch of read-only checkboxes immediately below the "copy notes button" (also, the copy notes button can be a lot smaller)


cut caffine pills in half
superglue headphone case
