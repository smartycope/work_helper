import argparse

from textual.containers import *
from textual.widgets import *

from HelperApp import HelperApp

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true')
args = parser.parse_args()

if __name__ == "__main__":
    app = HelperApp(debug=args.debug)
    try:
        app.run()
    finally:
        app.action_save()
