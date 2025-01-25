import argparse

from textual.containers import *
from textual.widgets import *
from time import sleep

from HelperApp import HelperApp

import keyboard

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true')
args = parser.parse_args()

def order_part_seq():
    """ enter, tab x3, "NA", tab, "NA", tab x2, enter """
    for key in ('enter', 'tab', 'tab', 'tab', 'N', 'A', 'tab', 'N', 'A', 'tab', 'tab', 'enter'):
        keyboard.press_and_release(key)
        if key != 'N':
            sleep(.01)


if __name__ == "__main__":
    app = HelperApp(debug=args.debug)
    try:
        keyboard.add_hotkey('ctrl+shift+k', order_part_seq)
        app.run()
    finally:
        app.action_save()
        keyboard.remove_all_hotkeys()
