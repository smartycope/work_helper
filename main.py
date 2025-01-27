import argparse
import atexit
from time import sleep

import keyboard
from textual.containers import *
from textual.widgets import *

from HelperApp import HelperApp

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true')
args = parser.parse_args()

def order_part_seq():
    """ enter, tab x3, "NA", tab, "NA", tab x2, enter """
    sleep(.2)
    for key in ('enter', 'tab', 'tab', 'tab', 'N', 'A', 'tab', 'N', 'A', 'tab', 'tab', 'enter'):
        keyboard.press_and_release(key)
        sleep(.05)


if __name__ == "__main__":
    app = HelperApp(debug=args.debug)
    atexit.register(app.action_save)
    keyboard.add_hotkey('ctrl+alt+k', order_part_seq)
    try:
        app.run()
    finally:
        app.action_save()
        keyboard.remove_all_hotkeys()
