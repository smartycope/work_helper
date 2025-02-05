from time import sleep
import keyboard, mouse, clipboard

def press_seq(*seq):
    for key in seq:
        keyboard.press_and_release(key)
        sleep(.05)

def order_part():
    """ enter, tab x3, "NA", tab, "NA", tab x2, enter """
    sleep(.2)
    press_seq('enter', 'tab', 'tab', 'tab', 'N', 'A', 'tab', 'N', 'A', 'tab', 'tab', 'enter')

def add_repair_report(case:str=None):
    """down, enter, tab, enter, (shift+tab, shift+tab, down, up, enter) OR (type current id, down, enter), tab, "Repair Report", tab, enter"""
    sleep(.2)
    press_seq('down', 'enter', 'tab', 'enter', *(case if case else clipboard.paste()), 'down', 'enter', 'tab', *'Repair Report', 'tab', 'enter')

def open_board(case:str=None):
    x, y = mouse.get_position()
    sleep(.05)
    mouse.move(150, 200)
    sleep(.1)
    mouse.move(150, 260)
    sleep(.05)
    mouse.click(button='left')
    sleep(.05)
    mouse.move(x, y)
    if case:
        press_seq(*('tab',)*3)
        keyboard.write(case)


"""
to goto board: hover over 150, 200 from top left, then delay like, half a second, then click on 150, 260
-- then, optionally, delay for page to load, then tab x3, and paste/type case id, and that filters for that case id
-- don't need to alt+tab

to search for case: go to board, shift+tabx7, paste case id, tab, enter
-- then, to actually get into the pick it up, right click 500, 470, and then very slight delay, and then click without moving



In the repair activities menu (the first step of alt+b):
130, 333 is the pick up case button (then immediately type the case id, then enter)
130, 370 is the return product button (shift+tab, then type case id, then enter)
130, 400 is the ship product button (type case id, then tab x 11, then enter)

388 × 205 is an empty space on the CSS window
936 × 142 is the query box (then tab, then enter, OR just enter. Try just enter first)


 """
