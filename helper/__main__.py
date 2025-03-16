import argparse
import atexit

from textual.containers import *
from textual.widgets import *

from helper.HelperApp import HelperApp
from globals import DEBUG


parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true')
args = parser.parse_args()

if __name__ == "__main__":
    DEBUG = args.debug
    app = HelperApp(debug=args.debug)
    atexit.register(app.action_save)

    try:
        app.run()
    except Exception as err:
        app.action_save()
        app.panic(err)
        # raise err
    finally:
        app.action_save()
        # keyboard.remove_all_hotkeys()


# Target size is 115x44
