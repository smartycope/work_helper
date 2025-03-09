Freaking do next TODOs:
    URGENT EXT: modify the "rusty bin screw" ext to dynamically say "clog" if M6, and also to modify the title
    HIGH NEXT: bump up priority for double clicking on todo box deletes the clicked on line. Would be very helpful

Step algorithm TODOs:
    URGENT: don't ask if the bot was cleaned if bot is non-modular, or M6
    HIGH: move asking for additional damage to be immediately before asking for the dock
    HIGH: don't ask if contacts are sunken if S9
    HIGH: if a battery test is needed, ask for it immediately before cleaning, instead of after
    HIGH: don't ask if blower play if r (or e) series

Mobility menu TODOs:
    HIGH: in the MM, when the dock type box is changed, if the cx has a dock, and it's not what it just got changed to, auto-change the "test/cx/new" dock param box to "test", UNLESS it was previously "new" and 'swap dock' (or equivalent) is in the notes (reuse the same condition as in the other todo)
    HIGH: in MM, if the "test/cx/new" dock param box is switched TO "cx", and there's a dock in the case, change the dock type param box to what the cx dock is
    HIGH: if bot didn't come in with a pad, assume new pad instead of cx pad
    HIGH: in MM, if lapis bin in parameters, and auto-evac is set to pass (True), then add "(didn't)" after auto evac after it
    HIGH: on opening the MM, focus on the first "where" select box
    MINOR: the "refill" MM disable should be and'd with if the current dock can refill or not (a C7 with an Albany shouldn't have it be enabled)
    MEDIUM: guess the mm cx bin param box each time reset based on regexing notes to find "move bin to new bot" and the like
    MEDIUM: add pad wash and pad dry to the MM, if the dock is a boulder
    MEDIUM: add a "clear" or "reset" all button to MM
    LOW: in MM, if "test dry pad" is selected, and only if it is, disable the tank param box
    LOW: in the MM, disable the cx box if the dock box is set to "no dock"

I don't want to do but probably should TODOs:
    URGENT: use ctrl+backspace instead of cltr+a, backspace to clear the filter box in open_board_dynamic()
    URGENT: printing cases on error isn't working
    MINOR BUG: allow ", l" to be a valid parts in, meaning no dock, lapis bin. test.
    URGENT: in parts in step, "alb, l" does not work -- test please
    URGENT: instead of logging on certain steps, log when it's opened, when it was closed, and the phase it was in when it was closed (hold vs accident vs finished)
    URGENT: add if repeat and adjustment to the log
    URGENT: figure out how to remove the delay in multi_paste()!
    DCT: if it's an R series and >=880, then specify that it's USB in the top side corner
    DCT EXP: for combo models, you may have to cover the vacuum with your hand during the vacuum test
    HINTS: add a sub-branch for evac problems: if it's evacing, and bin *actually* isn't getting cleared, then:
    HINT: battery auth problems: it's the robot, not the battery
    HINT: if the aurora white led flashes, it means the bot needs updated firmware

MINOR: prioritize other colors before yellow
MINOR: if the battery test step (I think in the method, maybe) just adds the input as notes instead, capitalize it
MINOR: change "am" to be an acronym instead of a command
MINOR: make the disabled background of the phase select box darker (via tcss!)
MINOR: in ext menu, if there's no dock, add "No Dock"
MINOR: change the color of the texts in the ext menu for cx dock and cx states to be something slightly darker. Or bolded. Just to distinguish it a little
MINOR: if one sn is i5g... and the other is not, use the one that is not as the official sn
MINOR: 90% is the bad battery cutoff: if a battery test is performed with <90% health, make the bullet ! and add "order new battery" to the todo box
MINOR LOW: disallow moving focus from input box if Step == pick up case on css
MINOR LOW: if m6, and not a refurb, don't ask if dry pad has been done
MINOR: make the "R" in the tab label stand out more somehow
MINOR HIGH: regex for ext notes for alex Albany warning: check if "alex" is in the 2nd line of the notes (and not "non")
MINOR: abstract adding notes to the TODO box into a method
MINOR: add optical failures to all dct exceptions, instead of just as the default
MINOR: combine step "clean dock" and "clean base"
MINOR: if ctrl+g is pressed while input box is already focused, jump to focusing on the text_area
MINOR: if the current bot (current serial) is non-modular, and bit is entered with no params, add "can't , as bot is non-modular" by default
MINOR: add icons appropriate icons to the phase select box items
MINOR: in the swap robot insert SN regex, only match if the line on the whole is less than super long
MINOR: if "pass mobility with lapis bin" (or the step before it, actually) have non-empty inputs, switch back to debugging phase
MINOR: decrease the width of the dock box 1 (the cx/new Select box), and have it stay to the right
MINOR: urgent submit event should trigger mobility submit like the other boxes
MINOR: if there's any mention of turn.+on in cx states, then offer a battery test
MINOR: don't add a newline to lapis bin warning if there's no other notes
MINOR: if "cleaned bot" step has a non-default resp, make the bullet a !
MINOR: readd ! as the default if non-empty resp for step "how do the customers base charging contacts look"
MINOR: add external notes regex to find if "charging contacts on ... - cleaned" (in routine checks), and if found, recommend cleaning dock charging contacts
MINOR: if there's more serial numbers than there were before, and that number is >1, default the mobility menu dock box to "new ..." instead of "cx ..."

HIGH: if entering swap phase, and "swap robot" or equivelent not in notes, auto add it (like ensure process)
HIGH: ask to test the battery after asking for the charging wattage on the cx dock
HIGH: switch "put on labels" to be immediately before "confirm ids" instead of after
HIGH: if sunken contacts, assume "recommend cleaning dock contacts" in EXT menu
HIGH: in battery test, allow an input ("low"?) to put in "Battery too low to test" instead
HIGH: move "check claimed damage" step to be immediately after "update css failure box" step
HIGH: ask for serial number in swap phase before ask to put on labels (have labels be last)
HIGH: if M6, ask if there's a pad, and if there is, add it to parts in
HIGH: if the bot doesn't charge on the cx dock, then ask if it charges on a test base
HIGH: attempt better guessing of floor (if can_mop, assume floor. If r or e series, assume top bench. otherwise, go with the setting -- also add "auto" to the floor setting)
HIGH: attempt better guessing of "new" dock box. If "swap dock" (or similar) in the notes, then guess new instead of cx/test
HIGH NEXT: add a setting to optionally go straight to charging phase from pickup case step
HIGH: in multi_paste, add a 2nd parameter of what to copy by default if it can't multi copy properly, then set them all
HIGH: add "add new case" and "close case" to the menu menu
HIGH: make saving each step a setting
HIGH: change "order a new dock" -> "order a new dock, if it's needed"
HIGH: make a setting to save every n minutes! You can do that with set_interval()
HIGH: on (before) "good to close case now" step in hold phase should save the case
HIGH: the ctrl+b LONG delay needs to read the color of a specific pixel
HIGH: check the claimed damage should be after the check the customer states
HIGH: squish together a bunch of the end steps, and also move back logging as far back as possible
HIGH: add a step, in confirm, but after "update css box" step, if repeat, to go see what the previous repeat was for
HIGH: when adding a date to the repeat email, note both the date the case was started, and when it was finished

HIGH: if theres not a bag in the dock when asked (and do the same for the pad when I get around to it), then set a variable and auto-add it once I get to debug phase to order/freebee a bag/pad
HIGH: do this order: claimed damage -> pickup & update failure box
HIGH: when opening a case, it should auto-set the step to "unbox" step, and the phase to "swap" -- also, auto-parse the "context" and add it to the todo box
HIGH: add a is_repeat member (not a property), and serialize it. Have it set by the "is teh case a repeat" step
HIGH: make the sidebar scrollable, and then drastically increase the size of the TODO box if the case is a repeat
HIGH: figure out some way to include whether the swap is a refurb or not
HIGH: Allow acronyms to specify the docks
HIGH: combine "close out parts and get out of case" with "fill in css" step
HIGH: copy case id for step "wait for parts to get closed out"
HIGH: add a step to color the box (if applicable) -- or just add onto a step
HIGH: merge "all done" last step into the "put on shelf" step
HIGH: remove or nullify all the phase if statements. They needlessly interrupt using "back" to go back to the previous step in a different phase
HIGH: in the new check voltage on the dock step, empty resp does not trigger a dock swap. Also, consider clarifying the text
HIGH: if the contact measurement is less than 3.8, round to 2 decimals instead
HIGH: move "order dock" to be immediately after instead of before step "reload case and order swap", and then also allow "reload case" to accept "hold" as a response, which automatically goes to the HOLD phase, and if a dock would have been asked about, auto add it to the HOLD context
HIGH: ensure_process() on changing phase to SWAP
HIGH: step "are the lid pins sunken" should accept na
HIGH: in external notes, if selected "rusty bin screw" (change the name first), then if M6, say "...can clog components" instead of rust
HIGH: figure out some way to accept entirely custom input to "how do the dock charging contacts look" step
HIGH: if bin screw is entirely rusted, automatically add the step under Process: Replaced bin -- maybe add a TODO I have to delete?
HIGH: just remove the "check for repeat" step entirely
HIGH: After I've switched to just adding CONTEXT after holding, auto-move the TODO text under context
HIGH: order dock *after* ordering a new bot (but if we do need to order a new dock, and it's a swap, then note that under CONTEXT)
HIGH: add another shortcut, just like alt+shift+k, but with 2 tabs instead of 3, and it pastes in the second box instead of "na"
HIGH: save case states, as well as plain files
HIGH: if it's the 2nd swap, skip some of the steps in the swap phase (like send swap email and unuse parts and the other one)
HIGH: if is_factory_lapis and the robot was swapped (there's more than one serial), then in finish phase ask if the bot's been removed from the app
HIGH: ctrl+end shortcut / fix all the shortcuts
HIGH: add backup states, and be able to load them
HIGH: give external notes menu open/close/toggle - or just make a Menu parent class
HIGH: when checking dock values, search the string instead of using == (alex-albany should still match Albany)
HIGH: in step " Found signs of liquid corrosion on the top board", if input is a single character, just assume motherboard
HIGH: replace the check SPL SKU step with a "check if tech box is needed" step
HIGH: move the menu_menu to the HelperApp, and have it pass it's events down to the active case manually
HIGH: M6 still asking about blower motor
HIGH: add a step in swap phase to put a tag on the new bot
HIGH: on start of the program, load the currently saved state file
HIGH: regex for extracting the dock from notes also captures the comma and space before it
HIGH: add a routine check for M6 specifically to check that the pad button works -- also add a step that asks how the filter looks
HIGH: mobility menu dock still using customer instead of cx (when using scraped dock info)
HIGH: on close of mobility menu, focus the end of the notes
HIGH: add a 2nd CopyText button for the other swap id, if there is one
HIGH: somehow emphasize C9's remove battery before CHM in notes
HIGH: cx stated charging error, and there was liquid damage, and did not ask for a battery test
HIGH: C9, Aurora, didn't ask to empty dock tank (I think, double check)
HIGH: auto guess the "where" in the mobility menu
HIGH: add a step (and make it the first step) in Finish phase, that asks if I've completed a successful mobility test, and attempted DCT
HIGH: when external notes menu opens via steps, it doesn't auto-load (call the open/toggle function instead of setting visible to True)
HIGH: add if the case has a lapis bin to notes -- and also that, if there's a lapis bin due to serial number, it doesn't need to be provisioned to the app to work
HIGH: in M6 bot, with no dock specified, it's asking if there's a bag in the dock - same case is asking if play
HIGH: if the case has a lapis bin, *in the serial number*, it should *not* suggest in external notes to reprovision bot to the lapis bin (and should even prevent it if it is checked, just disable it). But if the bot does *not* have a 7 in the serial, but *does* have one in the notes, (add a regex for it), then it *should* recommend reprovisioning, if a factory reset OR a swap
HIGH: phase deserialize doesn't load correctly
HIGH: add periodic saving
HIGH: in checking the user dock charging contacts, add the ability to include notes
HIGH: when doing a mobility test, if the dock specified is a base, not a dock, ask to confirm the bin does not have ad evac port, and if it should
HIGH: add ctrl+A to *all* input boxes

MEDIUM: allow debug mode to manually set attributes like repeat
MEDIUM: move asking if the case is a repeat to be before confirm IDs (immediately after pick up case)
MEDIUM: consider combining "put labels on everything" and "confirm ids" steps
MEDIUM: save the previous notes as well, so if "back" entered, it undos what was just done in the last step. Consider having the event triggered by manual editing the notes to None the prev_notes, so it doesn't do that if the user put stuff in
MEDIUM: organize acronyms better
MEDIUM: if "remove provisioning" already detected in the notes, don't ask to remove it in finish phase
MEDIUM: in "add any context about the case" step, if the resp is *not* empty, add it to the case just like add_step would. Only progress if it's empty.
MEDIUM: make RobotInfo allow multiple serials, and handle the serial property as well
MEDIUM: if an acronym is expanded at the beginning of a sentence, it doesn't get capitolized. fix that somehow
MEDIUM: if use "back" to go back to the add serial number step, it keeps adding serial numbers
MEDIUM: try disallowing num_lines can_focus
MEDIUM: if M6, in confirm, ask if there's a pad, and if there is, add it to the parts in
MEDIUM: in ext notes, if both "j7 and a swap" and "wake from shipping mode", then combine them together nicely
MEDIUM: if the name of one of the phases is entered exactly into the input box, switch to that phase (except swap, which adds "swap robot" and *then* switches)
MEDIUM: In routine checks, if the dock tank screw is entirely rusted, have the immediate next step be "order a new bin" (accepting na), and then add " - replaced" to the notes
MEDIUM: don't ask to clean an M6
MEDIUM: add a history of previous steps, so multiple "back"s works
MEDIUM: Pickup throws an error
MEDIUM: if a S9 is a swap due to liquid, don't say to just order a new chassis. Order a whole new bot.
MEDIUM: when ext indicates remove battery strip, it still is selecting wake from shipping mode
MEDIUM: change the external notes previews to be more descriptive, instead of describing the symptoms (i.e. don't say rusty bin screw, say recommend correct soap)
MEDIUM: if C9, and swap or order dock in a case, somehow make aware to swap with correct dock:
MEDIUM: I think multi paste fails when they try to interrupt each other - have multipaste remove any calls or anything before running
MEDIUM: Make "is there liquid damage" step allow for explanations, or just 'y' if simply "yes". Also, update the text to reflect this
MEDIUM: remove todo box can focus
MEDIUM: Auto-guess which test dock the mobility test will use
MEDIUM: add the current date somewhere, and don't update it. Also, add the name of the parent directory of main.py These together should work as a "version"
MEDIUM: if M6, in routine checks, ask if the filter is clogged at all
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
MEDIUM: torino asked about bag in the dock in the finish phase
MEDIUM: CopyText needs some sort of feedback when pressed (lighten background like regular buttons do)
MEDIUM: make the lower sidebar butt against the bottom properly
MEDIUM: J955 - 1st 5 means evac dock, 1 means base. 2nd 5, if 7, means lapis bin
MEDIUM: Consider a "clear TODO" button (or at least make it select everything on focus)
MEDIUM:  make the DCT card a single line
MEDIUM: in external notes menu, disable certain options based on the bot's model
MEDIUM: don't ask about the blower motor on R series bots
MEDIUM: Add an indicator to the tabs when the case is finished
MEDIUM: in mobility mission menu and combo (not can_mop), ask if tank is full
MEDIUM: add a button to open the case in css
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

LOW: add print statements to all/most/some of the hotkeys (can't hurt)
LOW: the order (after being reordered) isn't saved, apparently? more testing needed
LOW: somehow disallow focusing of anything outside of a menu when it's open
LOW: figure out some way to have it "restart" itself (fully)
LOW: add some way of regexing serials from notes
LOW: in step "robot charges on test base ...", if S9/M6, specify the actual dock by name
LOW: make "back" work with multiple steps (add an undo stack)
LOW: if double click a line in the TODO sidebar box, it deletes the whole line
LOW: add a setting to make colors optional
LOW: add a red (or alerting) border to the todo box if there *is* text in it
LOW: make the rest of the window dim when a Menu is open
LOW: only allow one window to be open at a time
LOW: if "pass" is in the bit output step (when expanded
LOW: make a keyboard shortcuts menu
LOW: some way to remove serial numbers/swaps
LOW: also set the tooltip of the input box to be what's in it, cause why not
LOW: if a repeat, add a 2nd ref CopyText
LOW: move external notes to the menu menu, instead of as a binding, it doesn't need a shortcut anymore
LOW: add after_ and before_ method lookups for phases just like I have for steps (to automate adding headers like Process: and CONTEXT: and Routine Checks:)
LOW: if the serial numbers are different lengths, add to the text area, in addition to what's already there: "did you forget to scan both serial numbers one after another?"
LOW: remove all useless comments and clean up code
LOW: figure out how to remove the ^p shortcut on the right side of the footer
LOW: for the step "sidebrush is on and screws are tight" make the "sidebrush is on" part be a formatted portion dependant on if it's not an M6
LOW: don't ask to put the bin pack for M6 -- might not be relevant by time I get to this
LOW: when measuring contacts, if the measurement is close (say, within .15 mm), then state how many measurements were taken
LOW: a different background/main color for the hold emoji would be nice (blue is already for swap)
LOW: add another measure to log, which is how long each case is actually open for
LOW: figure out how to darken the last space of the tabs
LOW: in the step "take tags off bin and dock", move the "and dock" into a conditional formatted step string if there is a dock
LOW: add mobility test step to debugging phase
LOW: make a new class, something like AttentionText, which blinks until you click on it, then it stops
LOW: clean chirp sensor holes, if needed
LOW: some sort of reminder to clean the bin sensors: especially if they come in with bin not clearing and/or evac issues
LOW: If swap, copy the robot's defective serial number
LOW: if it's a big base, and it's any sort of vacuum stall or filter clog or something, remind to check the dock evac channel
LOW: ctrl + backspace doesn't seem to work
LOW: on focus (window focus, at least), the input shouldn't select all of it's text
LOW: if only a single number is put into the battery test step, assume health is 100%
LOW: clean up the flowchart
LOW: make a 2nd shortcut for 1 tab vs 2 in the order part shortcut
LOW: make it so it finds where it should put text, so lower down I can manually add notes and it won't keep just adding to the end
LOW: add a switch to mobility menu to indicate testing a swapped bot
LOW: add a requirements.txt file
LOW: instead of manually uppercasing strings, turn it into a function, and don't un-uppercase the string if the 2nd letter is uppercase (we don't want "cHM is...")
LOW: consider refactoring all the private members into public properties, that return self._member or regex to find it if self._member is None
LOW: a button to allow you to reset the name of the dock
LOW: clean up all the comments and things
LOW: disallow unfocusing new case input box when visible
LOW: don't ask about sunken contacts on an S9 specifically
LOW: strip all input box text
LOW: confirm closing a case
LOW: ctrl + t is toggle case
LOW: add some way to specify no evac bag in claimed damage instead of in visible damage
LOW: add some way to manually go to a specific step
LOW: click at 420, 470 immediately before step "update css failure code"
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
LOW: the colors of the CopyText buttons are arbitrary: make the text color the color of the case
LOW: make a simple script I can give to everyone else that just confirms the IDs, and prints all the relevant information for that model (the sidebar stuff)
LOW: in the mobility menu, have the outline reflect whether the ultimate result is a pass or fail (with red/green)
LOW: add "add new case" to the menu menu
LOW: if no dock indicated on dock (in mobility menu), then auto-unselect dock and undock sliders
LOW: in add_step(): if the previous line has "** Result: " in it, add an extra line -- maybe
LOW: on double check, add "double checked by michelle" to the notes (and then recopy the notes into CSS)
LOW: Add a readme with run instructions and the like
LOW: if the text_area ends in "* ", remove it as well
LOW: See if bot charges on customer dock BEFORE battery test (if both applicable)
LOW: If a bot needs a battery test, ask about it immediately before cleaning
LOW: change/check the shade of blue
LOW: add detailed installation instructions on the README
LOW: clean up the flowchart more

TEST: ALL THE TESTS
TEST: dct exceptions
TEST: adding text manually
TEST: for changing color
TEST: adding 5 cases all at once
TEST: tests for combos vs non-combos
TEST: tests for seralizing/deserializing

EPIC: handling duplicate cases
EPIC: in all the try except statements, if there's an error caught and there *shouldn't* be, log it in the interal log file (I'm thinking specifically of the one if it can't save)
EPIC: autocorrect, somehow?
EPIC: color the notes
EPIC: add settings menu, with the following settings:
EPIC: reintegrate double check better

SETTING: parts are being run (determines if we should ask if the parts have been closed out yet or not)

UX: readd TODO label in sidebar (or equivalent)
UX: add a disclaimer in the ext notes menu stating that this is not definitive, and usually needs editng, and you should always double check it, etc.
UX: add a "tutorial mode" setting, which, if set, add explanations to the input box based on the step (and also write all the explanations)
UX: add a settings file. initialize if doesn't exist, otherwise just load it
UX: if in tutorial mode, add a tooltip to the new case Input box (first, see how intrusive and annoying tooltips are)
UX: instead of disallowing phase to change if haven't picked up the case yet, instead just disable the box
UX: if no dock is specified, disable the cx/test/new param box
UX: add more explanations (and examples) in command and acronym menus
UX: add a caviat in ext menu to absolutely only select what you actually did

REFACTOR: abstract the ext notes into a JSON file
REFACTOR: the TODOs above RobotInfo

WEB REFACTOR: add a global web member that gets auto-set somehow
WEB: if web version, don't include any of the hotkey bindings
WEB: if web version, change the bindings to work (ctrl+n, ctrl+w, for starters)
WEB: remove the date display thing I was using for versioning, and add *real* versioning.

UNRELATED:
Look up:
"the others" by Jeremy robinson
"schrodinger's killer app"
blog: "cheatle optimized" (phontetic)

Ask about how adjustments work for repeats that go on hold

"b" assumes "Torino" instead of "Bombay"?? interesting.
