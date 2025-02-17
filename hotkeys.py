from time import sleep
import keyboard, mouse, clipboard

LONG = 1
SHORT = .05
START_DELAY = .2


def press_seq(*seq):
    for key in seq:
        keyboard.press_and_release(key)
        sleep(SHORT)

def order_part():
    """ enter, tab x3, "NA", tab, "NA", tab x2, enter """
    sleep(START_DELAY)
    press_seq('enter', 'tab', 'tab', 'tab', 'N', 'A', 'tab', 'N', 'A', 'tab', 'tab', 'enter')

def order_swap():
    """ enter, tab x2, "NA", tab, paste, tab x2, enter """
    sleep(START_DELAY)
    press_seq('enter', 'tab', 'tab', 'tab', 'N', 'A', 'tab', 'ctrl+v', 'tab', 'tab', 'enter')

# TODO: this needs work
def add_repair_report(case:str=None):
    """down, enter, tab, enter, (shift+tab, shift+tab, down, up, enter) OR (type current id, down, enter), tab, "Repair Report", tab, enter"""
    sleep(START_DELAY)
    press_seq('down', 'enter', 'tab', 'enter', *(case if case else clipboard.paste()), 'down', 'enter', 'tab', *'Repair Report', 'tab', 'enter')

# This is fairly reliable
def open_board(case:str=None):
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
    if case:
        press_seq(*('tab',)*3)
        keyboard.write(case)

def open_ship_product(case:str=None):
    x, y = mouse.get_position()
    sleep(SHORT)
    mouse.move(150, 200)
    sleep(.1)
    mouse.move(150, 400)
    sleep(SHORT)
    mouse.click(button='left')
    sleep(SHORT)
    mouse.move(x, y)
    sleep(LONG)
    if case:
        keyboard.write(case)
    else:
        press_seq('ctrl+v')
    press_seq(*('tab',)*11, 'enter')

def open_return_product(case:str=None):
    x, y = mouse.get_position()
    sleep(SHORT)
    mouse.move(150, 200)
    sleep(.1)
    mouse.move(150, 370)
    sleep(SHORT)
    mouse.click(button='left')
    sleep(SHORT)
    mouse.move(x, y)
    sleep(LONG)
    keyboard.press_and_release('shift+tab')
    sleep(SHORT)
    if case:
        keyboard.write(case)
    else:
        press_seq('ctrl+v')
        sleep(SHORT)
        keyboard.press_and_release('enter')

def query_case(case):
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

388 × 205 is an empty space on the CSS window
936 × 142 is the query box (then tab, then enter, OR just enter. Try just enter first)

Previous loaded menu color invalid! New is #272b30 @ 316 × 309

after entering ship menu, tab x7, then (enter, down) x3

Menu loading background color: #131518

Default background CSS color is #272b30
CSS loaded board has #272b30 @ 100, 860 and #3e444c @ 50, 782
CSS all the loaded menus should have #272b30 @ 100, 860

! the quick search box location is unreliable!

"""
