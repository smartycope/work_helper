""" Automatic control functions for my specific setup of CSS. They only use the mouse to click on the
main drop down menu, everything else is nice, deterministic key presses, mostly navigating via tab.
These are only meant to be used by me.
"""

from time import sleep, monotonic
import keyboard, mouse, clipboard
import pyautogui

LONG = 1
SHORT = .05
START_DELAY = .2

# 388 × 205 is an empty space on the CSS window
# EMPTY_SPACE = 388, 205
EMPTY_SPACE = 50, 831

def press_seq(*seq, delay=SHORT):
    for key in seq:
        keyboard.press_and_release(key)
        sleep(delay)

def order_part():
    """ enter, tab x3, "NA", tab, "NA", tab x2, enter """
    sleep(START_DELAY)
    press_seq('enter', 'tab', 'tab', 'tab', 'N', 'A', 'tab', 'N', 'A', 'tab', 'tab', 'enter')

def order_swap():
    """ enter, tab x2, "NA", tab, paste, tab x2, enter """
    sleep(START_DELAY)
    press_seq('enter', 'tab', 'tab', 'tab', 'N', 'A', 'tab', 'ctrl+v', 'tab', 'tab', 'enter')

# This is old, don't use it. use add_case instead
def add_repair_report(case:str=None):
    """down, enter, tab, enter, (shift+tab, shift+tab, down, up, enter) OR (type current id, down, enter), tab, "Repair Report", tab, enter"""
    sleep(START_DELAY)
    press_seq('down', 'enter', 'tab', 'enter', *(case if case else clipboard.paste()), 'down', 'enter', 'tab', *'Repair Report', 'tab', 'enter')

# This is fairly reliable
def open_board(case:str=None, guess_from_clipboard=False):
    sleep(START_DELAY)
    x, y = mouse.get_position()
    sleep(SHORT)
    mouse.move(150, 200)
    sleep(.1)
    mouse.move(150, 260)
    sleep(SHORT)
    mouse.click(button='left')
    sleep(SHORT)
    mouse.move(x, y)
    sleep(LONG)

    if not case and guess_from_clipboard:
        p = clipboard.paste()
        if len(p) == 7 and p.lower().endswith('ir'):
            case = p

    if case:
        press_seq(*('tab',)*3)
        keyboard.write(case)

def open_board_dynamic(case:str=None, timeout_sec=10, guess_from_clipboard=False, end_mouse_loc=(472, 449)):
    """ make end_mouse_loc None to end the mouse where it started """
    sleep(START_DELAY)
    print('-'*20)
    # if 24 × 325 is #f0f8f8 - #f0f0f0, it's in the main board
    in_board = lambda tolerance=10: pyautogui.pixelMatchesColor(24, 325, (244, 244, 244), tolerance=tolerance) # 5 should be enough

    # Don't load the board if we're already there
    x, y = mouse.get_position()
    if not in_board():
        # started_in_board = False
        print('not in board, going to board')
        sleep(SHORT)
        mouse.move(150, 200)
        sleep(.1)
        mouse.move(150, 260)
        sleep(SHORT)
        mouse.click(button='left')
        sleep(SHORT)
        # mouse.move(x, y)

        start = monotonic()
        while monotonic() < start + timeout_sec:
            print('waiting until board is loaded...')
            if in_board():
                print('board loaded!')
                break
            sleep(SHORT)
    # else:
    # started_in_board = True
    # Still make sure the right window is open
    print('board is open, clicking on window')
    mouse.move(*EMPTY_SPACE)
    sleep(SHORT)
    mouse.click(button='left')
    sleep(SHORT)

    if end_mouse_loc is None:
        mouse.move(x, y)
    else:
        mouse.move(*end_mouse_loc)

    # If we weren't given a case, but one is loaded in the clipboard, use it
    if not case and guess_from_clipboard:
        p = clipboard.paste()
        if len(p) == 7 and p.lower().endswith('ir'):
            print('loading case from clipboard')
            case = p

    if case:
        print('filtering case')
        # press_seq(*('tab',)*(5 if started_in_board else 3), 'ctrl+a', 'backspace')
        #press_seq(*('tab',)*5, 'ctrl+backspace')
        press_seq('shift+tab', 'ctrl+backspace')
        keyboard.write(case)
    else:
        print('no case provided or inferred, done')


def open_ship_product(case:str=None):
    # x, y = mouse.get_position()
    sleep(SHORT)
    mouse.move(150, 200)
    sleep(.1)
    mouse.move(150, 400)
    sleep(SHORT)
    mouse.click(button='left')
    # sleep(SHORT)
    sleep(LONG)
    if case:
        keyboard.write(case)
    else:
        press_seq('ctrl+v')
    press_seq(*('tab',)*11, 'enter')

    # mouse.move(x, y)
    mouse.move(827, 503)

def open_return_product(case:str=None):
    # x, y = mouse.get_position()
    sleep(SHORT)
    mouse.move(150, 200)
    sleep(.1)
    mouse.move(150, 370)
    sleep(SHORT)
    mouse.click(button='left')
    # sleep(SHORT)
    # mouse.move(x, y)
    sleep(LONG)
    keyboard.press_and_release('shift+tab')
    sleep(SHORT)
    if case:
        keyboard.write(case)
    else:
        press_seq('ctrl+v')
        sleep(SHORT)
        keyboard.press_and_release('enter')
    mouse.move(1192, 836)


# TODO: the position of the query box is unreliable
def query_case(case=None):
    return
    mouse.move(388, 205) # Empty spot on the window
    sleep(SHORT)
    mouse.click(button='left')
    sleep(SHORT)
    mouse.move(936, 142) # Query box
    sleep(SHORT)
    mouse.click(button='left')
    sleep(SHORT)
    keyboard.write(case)
    sleep(SHORT)
    keyboard.press_and_release('enter')

def search_for_swap():
    """ ctrl+a, backspace, tab x2, down x2, enter, tab, space, tab x2, enter """
    # try alt+f
    sleep(START_DELAY)
    press_seq('ctrl+a', 'backspace', 'tab', 'tab', 'down', 'down', 'enter', 'tab', 'space', 'tab', 'tab', 'enter')
    mouse.move(125, 407)

def add_case(case=None):
    """ starting from the description box,
    "repair report", shift+tab, enter, wait, case id, ".pdf", enter, wait short, shift+tab,
    down x2, enter, tab x3, enter, done
    """
    sleep(START_DELAY)
    keyboard.write('Repair Report')
    sleep(SHORT)
    press_seq('shift+tab', 'enter')
    sleep(.75)
    if case:
        keyboard.write(case)
    else:
        press_seq('ctrl+v')
    keyboard.write('.pdf')
    sleep(SHORT)
    press_seq('enter')
    sleep(SHORT)
    press_seq('shift+tab', 'down', 'down', 'enter', 'tab', 'tab', 'tab', 'enter')



"""
to goto board: hover over 150, 200 from top left, then delay like, half a second, then click on 150, 260
-- then, optionally, delay for page to load, then tab x3, and paste/type case id, and that filters for that case id
-- don't need to alt+tab

to search for case: go to board, shift+tabx7, paste case id, tab, enter
-- then, to actually get into the pick it up, right click 500, 470, and then very slight delay, and then click without moving



In the repair activities menu (the first step of alt+b):
//130, 333 is the pick up case button (then immediately type the case id, then enter)
130, 370 is the return product button (shift+tab, then type case id, then enter)
130, 400 is the ship product button (type case id, then tab x 11, then enter)


936 × 142 is the query box (then tab, then enter, OR just enter. Try just enter first)

Previous loaded menu color invalid! New is #272b30 @ 316 × 309

after entering ship menu, tab x7, then (enter, down) x3

Menu loading background color: #131518

Default background CSS color is #272b30
CSS loaded board has #272b30 @ 100, 860 and #3e444c @ 50, 782
CSS all the loaded menus should have #272b30 @ 100, 860

! the quick search box location is unreliable!

 This is now unreliable, as more holds get put on
// CSS loaded board has #272b30 @ 100, 860 and #3e444c @ 50, 782
 if 24 × 325 is #f0f8f8 - #f0f0f0, it's in the main board
"""
