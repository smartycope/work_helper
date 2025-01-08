import argparse
from collections import OrderedDict

from textual.containers import *
from textual.widgets import *

from HelperApp import HelperApp

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true')
args = parser.parse_args()

SIDEBAR_WIDTH = 30
COPY_SERIAL_BUTTON_WIDTH = 8
COLORS = OrderedDict((
    ("#377a11", "Green"),
    ("#ef9e16", "Orange"),
    ("#d1dd0b", "Yellow"),
    ("#ea9daf", "Pink"),
    ("#799fad", "Blue"),
))

# if args.debug:
#     with open('~/Documents/deleteme_log.txt', 'w') as f:
#         f.write('')

#     _print = print
#     def print(*a, **kw):
#         with open('~/Documents/deleteme_log.txt', 'a') as log:
#             _print(*a, file=log, **kw)





if __name__ == "__main__":
    app = HelperApp(debug=args.debug)
    try:
        app.run()
    finally:
        app.action_save()

    # if args.debug:
    #     with open('~/Documents/deleteme_log.txt') as f:
    #         _print(f.read())
