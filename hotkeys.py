from time import sleep
import keyboard
import clipboard

def order_part_seq():
    """ enter, tab x3, "NA", tab, "NA", tab x2, enter """
    sleep(.2)
    for key in ('enter', 'tab', 'tab', 'tab', 'N', 'A', 'tab', 'N', 'A', 'tab', 'tab', 'enter'):
        keyboard.press_and_release(key)
        sleep(.05)

def add_repair_report_seq():
    """down, enter, tab, enter, (shift+tab, shift+tab, down, up, enter) OR (type current id, down, enter), tab, "Repair Report", tab, enter"""
    sleep(.2)
    for key in ('down', 'enter', 'tab', 'enter', *clipboard.paste(), 'down', 'enter', 'tab', *'Repair Report', 'tab', 'enter'):
        keyboard.press_and_release(key)
        sleep(.05)

keyboard.add_hotkey('ctrl+alt+k', order_part_seq)
keyboard.add_hotkey('ctrl+alt+l', add_repair_report_seq)
