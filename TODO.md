TODO
clean optical bin sensors
mobility test
bbk
dct
clean chirp sensor holes, if needed
non-modular i5's are different
add an option to not check battery and things like that (detect na)
check if wheels click good?
swapping checklist

remind that older robots, when testing, need to be activated manually
battery test input should allow splitting on whitespace as well

Make note that J5, J6 ,& J7, if it just boots (white light spins) indefinitely, then you need to replace the *battery*, with one of the following SKUs (in order of preference):
4706313
4763362           
4785636
4624864
This is caused by firmware version 24.29.1


If swap, copy the robot's defective serial number
DONE: if bot is a combo, check for rust (and don't check for liquid damage)
if it's a big base, and it's any sort of vacuum stall or filter clog or something, remind to check the dock evac channel


when finishing, and a combo, remind to clean pad and under the pad

if charging issue, final check the charging wattage

ctrl + backspace doesn't seem to work
    ability to change colors on cases
The whole sidebar color is a little glaring
autocapitalizing
on focus (window focus, at least), the input shouldn't select all of it's text
make it so it finds where it should put text, so lower down I can manually add notes and it won't keep just adding to the end
if it's a mopping model (m* serial number), don't ask a lot of the routine questions
at the end, add the "process" section
esc should cancel the new case dialog
change/check the shade of blue
make it cycle through colors better
reorder colors
check sunken contacts *before* cleaning (removing the bottom)
when asking if the user charging docks are good, add an option to say I cleaned them
add mobility test before going directly to add_step (later)
ask if rollers are good immediately after cleaning
check if user charging contacts are good needs an "(empty for yes)"
forcibly disallow multiple lines of whitespace between lines that start with *
some sort of reminder to clean the bin sensors: especially if they come in with bin not clearing and/or evac issues
if we measured one contact, and it's good, ask if the other one needs to be measured as well
always keep 1 newline at the end of the text
i series factory reset is wrong
Show the phase somewhere
finish phase
when textarea is focused, it should always put the cursor at the very end
Add a section for TODO?
only show notes if there is notes
strip input box text
confirm closing a case
have an option to create a case and just paste stuff in, instead of starting from the beginning
If its any sort of auto-evac problem, clean the bumper
strip the copied string (copy button)
Add some toasts? (copied, pick up case, case ref copied, etc)
it's asking about the user contacts without self.base being true
Consider an option to reopen a case
autofocus to input box on tab switch
make the tab switch shortcuts show=False
Allow multicolored tabs
put customer states immediately after picking up case instead
add an option to say non-modular when checking for liquid (or first thing to open the back)
ctrl+home/ctrl+end
no sign of liquid *resudue* (not damage)
If I ever type "cancel", just go directly to "add step"

ctrl + t is toggle case
IF the robot doesn't turn on at all (i.e. liquid damage), test the battery
double click select word

J955 - 1st 5 means evac dock, 1 means base. 2nd 5, if 7, means lapis bin
warn if the robot has an evac bin and/or dock, and I haven't mobility tested with evac bin, or with customers dock

highlight DCT colors?
maybe just ask if a battery test is needed?

remind to put in the new robot's serial number, if a swap occurs
remind to pout in sleep mode
maybe have up and down keys put the previous lines in the input box to edit

if the text_area ends in "* ", remove it as well
remind to stick DCT cable under the mop pad in combo modles
remind to empty bin before shipping on combo modles

clean optical bin sensors
mobility test
bbk
dct
clean chirp sensor holes, if needed
non-modular i5's are different
add an option to not check battery and things like that (detect na)
check if wheels click good?
swapping checklist
 *
remind me to bring traveler when doing a battery check
Display current phase, to make context switching easy
remind that older robots, when testing, need to be activated manually
make routine checks that dont pass start with !
sub checks (like for liquid) should start with **
battery test input should allow splitting on whitespace as well

DCT known failures:
J-Series robots with FW version 24.29.x will fail test #2 dock comms.
○ Ensure robot will evacuate and ignore DCT dock comms failure
● S9 robots may fail vacuum tests with low-current above 1000.
○ Ignore as long as value is below 1500
● Some robots will fail optical bin tests. 2 failures allowed, as long as the values are close
○ E.G. 500-1000 and the robot fails with 490.
● Pad detection tests on the M6 will sometimes fail.
○ Ignore if both wet and dry mobility missions are successful.
● C7 and C9 robots will fail actuator arm with FW’s higher that 23.53.6
○ As long as the actuator arm will deploy normally during mobility and the failures
are for speed and range, ignore DCT.
● Battery charging will fail on a full battery
○ Ignore if you know the battery State of Charge is high.


If swap, copy the robot's defective serial number
if bot is a combo, check for rust (and don't check for liquid damage)
check if the blower motor spins freely as well
if it's a big base, and it's any sort of vacuum stall or filter clog or something, remind to check the dock evac channel

when finishing, and a combo, remind to clean pad and under the pad
automaqtically assign colors to cases, so i can use multicolored markers to keep track easily

if charging issue, final check the charging wattage

a "cancel out of the prewritten script" option
ctrl + backspace doesn't seem to work
dct breaks on "C9C9"
definitely make the sidebar smaller
add ctrl+s to save
remind to check tank bin screw on combo models
ability to change colors on cases
The whole sidebar color is a little glaring

on focus (window focus, at least), the input shouldn't select all of it's text
make it so it finds where it should put text, so lower down I can manually add notes and it won't keep just adding to the end
if it's a mopping model (m* serial number), don't ask a lot of the routine questions
at the end, add the "process" section
esc should cancel the new case dialog
change/check the shade of blue
check sunken contacts *before* cleaning (removing the bottom)
when asking if the user charging docks are good, add an option to say I cleaned them
add mobility test before going directly to add_step (later)
ask if rollers are good immediately after cleaning
check if user charging contacts are good needs an "(empty for yes)"
forcibly disallow multiple lines of whitespace between lines that start with *
some sort of reminder to clean the bin sensors: especially if they come in with bin not clearing and/or evac issues
if we measured one contact, and it's good, ask if the other one needs to be measured as well
always keep 1 newline at the end of the text
i series factory reset is wrong
Show the phase somewhere
finish phase
when textarea is focused, it should always put the cursor at the very end
Add a section for TODO?
only show notes if there is notes
strip input box text
confirm closing a case
have an option to create a case and just paste stuff in, instead of starting from the beginning
If its any sort of auto-evac problem, clean the bumper
strip the copied string (copy button)
Add some toasts? (copied, pick up case, case ref copied, etc)
it's asking about the user contacts without self.base being true
Consider an option to reopen a case
autofocus to input box on tab switch
make the tab switch shortcuts show=False
Allow multicolored tabs
put customer states immediately after picking up case instead
add an option to say non-modular when checking for liquid (or first thing to open the back)
ctrl+home/ctrl+end
no sign of liquid *resudue* (not damage)
If I ever type "cancel", just go directly to "add step"

ctrl + t is toggle case
IF the robot doesn't turn on at all (i.e. liquid damage), test the battery
double click select word

J955 - 1st 5 means evac dock, 1 means base. 2nd 5, if 7, means lapis bin
warn if the robot has an evac bin and/or dock, and I haven't mobility tested with evac bin, or with customers dock

highlight DCT colors?
maybe just ask if a battery test is needed?

remind to put in the new robot's serial number, if a swap occurs
remind to pout in sleep mode
maybe have up and down keys put the previous lines in the input box to edit

if the text_area ends in "* ", remove it as well
remind to stick DCT cable under the mop pad in combo modles
remind to empty bin before shipping on combo modles


# Split everything into functions
# add comments
# make it easily updatable
# consider using rich or something to make it even more easy to use
# Make absolutely sure that if it fails, it still prints and copies the current report
# add more modes and things
# parse docks and get information
# add an information section
# LOTS of testing
# Get robot nicknames
# remind to scan the new swap ID
# maaaybe pyautogui
# lots of different entrypoints
# a dict? of cases
# swap sunken and liquid damage checks
# ask for any cleaning notes
# if charge wattage is 2-6, battery is likely already charged
# add paper reference tag to bot and base
# if J7 flint variant (blue dct card) doesn't work, then: disconnect battery, hold down the clean button for 20 seconds, then reboot, factory reset, wait, and try to connect it again
# have a factory reset flag, so if I do, it remembers to tell the user on external notes
# see if I can get an error reference built in
# add step to check if dock has a bag
# make all the steps inturruptable
# add chargining notes
# change dict accessors to .get() calls
# Bug: 'c' not found in some dict
# auto capitalize notes
# if not charging, don't put the wattage
# autocorrect, somehow?
# put in the notes if contacts are not sunken
# combine both steps into one section called "Process", and just stick a diagnosis in there somewhere


# customer notes
#*** Replaced Robot ***
#Replaced robot with equivalent model.


#*** Recommendations ***
#Recommend regular cleaning and maintenance.

#Recommend regular cleaning of dock charging contacts.

#Recommend regular cleaning of the bin filter.


#*** Parts ***
#Recommend using only OEM replacement bags.


#*** Shipping ***
#Please place robot on dock to wake from shipping mode.

#Remove yellow slip underneath robot once received to activate.

#Factory reset performed, recommend re-provisioning robot on app.

#J7's, if a swap (due to the client's dock might have outdated firmware):
#Please provision robot to application.


#*** MISC ***
#We have upgraded your battery to a ____ mAh battery with higher capacity, you may notice a visible difference from your original battery, should you open the battery compartment.

test dct exceptions
Always keeping a single newline at the end of the text isn't working - test this
test adding text manually
remove the todo box margins, if possible

NEXT: make UI for mobility tests:
I think I want the mobility test to be formatted like this:

* 2nd Mobility test - floor, new Aurora, empty bin
** Pass: undock, clean | Fail: refill, pad deploy | Result: Fail
** Notes ntoes notes

options: undock, dock, "navigate" (instead of clean), pick up rice, other, refill, auto-evac, manual evac, pad deploy, number of water lines, is streaky


Number the mobility tests automatically
consider having a preview of what the mobility test entry will look like

Make swap have a bunch of separators (i.e. *************** Swap ***************)

Consider a "clear TODO" button (or at least make it select everything on focus)
check what DCT card j9 uses
Low priority: Add some color to the notes area to make things easily distinguishable (but make sure not to copy it!)

add a in notes that if it's a C9, and I can't get DCT to work, to pull the battery out, and hold the clean button down for 10 seconds, then reboot

At the end, do a bunch of regex on the notes and confirm that I'm not forgetting anything -- including adding in the customer notes that a factory reset was performed

for sleep mode on C9, remove the "and press again to confirm"

Tests for changing color

on focus, the text area should always move the cursor to the very end
add a "can close" variable to case

remove the margins on the serial copy button

URGENT: add a method to move cases to updated version ("copy all" and "paste all" buttons, I'm thinking) -- also, make it save when the cases do

URGENT: add periodic saving

URGENT: ctrl+end shortcut

Add to notes that J9s, as well as C9s, can need hard reset to get DCT to work

test not same ids

URGENT: Move the model next to the case ref, and make the DCT card a single line

LOW PRIORITY: a find shortcut

hide copy binding in text_area footer

make sidebar 25% of the overall width, with a min width

in the play in blower motor task, say in notes that it spins freely

say explicitly that the extractors look good

I need to be able to close cases partway through due to lack of parts

LOW PRIORITY: Bold the 3 middle characters of the ref id?

capitalize copied serial num

Try adding shift+ctrl be delete word left

make the ** -> ***


make the add_step() method strip the text and then readd whitespace to ensure it's always correct

LOW PRIORITY: add if the dock or bot have been swapped next to the TODO box for context

add shortcut to jump to input box

Add an indicator to the tabs when the case is finished

J9 is in fact the blue card

test adding 5 cases all at once

add a way to change the serial number

make the sidebar be 30% instead of 25%

change close case to ctrl+W

whenever i get to swap logic, check to see if the in stock SPL (refilter for all bots) is in stock, or if there's an upgrade available

add a is_mopper property to Case

I think maybe newline adder is getting too ambitious?

Automatically scroll to the end of the text_area after adding a step


I can auto remove lines if there's 3 newlines in a row

add some sort of input parsing for tank screw rust to indicate if there's a spot of rust, no rust, or lots of rust

Low Priority: maaaybe try to auto generate and send the swap email

Make note that if I can't get BBK to work, I can ask Michelle to look it up on RDP (as a double check final step)

in mobility mission menu and is_mopping, as if tank is full

reset mobility count after a swap

for contact measurements, add an option to take a number of them, then average and std them together

back broke

in confirm checks, remind to enter the failure code to CSS and maybe show what "customer states" is for reference

in checking the user dock charging contacts, add the ability to include notes

only c9's can refill

tests for combos vs non-combos

tests for seralizing/deserializing

save serialzed state to a file in action_save()`212qw

serialization should include the current phase

make swapping a phase

unuse any parts before sending swap email!

add a warning or something if characters exceed 4000

if FW >= v24.29.5 on C9 (and C7?), DCT exception: can't run at all

add a double check phase, after finish, that regexes everything. Include:
factory reset
swap
dct

See if bot charges on customer dock BEFORE battery test (if both applicable)

i series: if having weird trouble with DCT, try factory reset

which side (sunken) add "both"

bad contact should go to swap phase, instead of finish phase

make diagnosis back to - instead of *

immediately after customer states, go to a new step: "update case failure code on CSS"

If there's a bad contact, still check the battery if I need to

disable tests based on serial number

close case from input box
