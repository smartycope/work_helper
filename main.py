import argparse
import atexit
import keyboard

from textual.containers import *
from textual.widgets import *

from HelperApp import HelperApp
from globals import LOG_PATH
# import hotkeys


parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true')
args = parser.parse_args()

if __name__ == "__main__":
    app = HelperApp(debug=args.debug)
    atexit.register(app.action_save)

    try:
        app.run()
    except Exception as err:
        app.panic(err)
        # raise err
    finally:
        app.action_save()
        # keyboard.remove_all_hotkeys()


# Target size is 115x44
