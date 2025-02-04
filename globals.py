from collections import OrderedDict
from pathlib import Path

Documents = Path.home() / 'Documents'
LOG_PATH = Documents / 'helper_log.csv'
SAVE_CASE_PATH = Documents / 'Case_Notes'
SAVE_STATE_PATH = Documents / 'helper_state.json'

# TODO:
# for path in (SAVE_CASE_PATH, SAVE_STATE_PATH):
#     path.mkdir(parents=True, exist_ok=True)

SIDEBAR_WIDTH = 30
COPY_SERIAL_BUTTON_WIDTH = 8
COLORS = OrderedDict((
    ("#377a11", "Green"),
    ("#ef9e16", "Orange"),
    ("#d1dd0b", "Yellow"),
    ("#ea9daf", "Pink"),
    ("#799fad", "Blue"),
))

def invert_dict(d:dict) -> dict:
    """ Returns the dict given, but with the keys as values and the values as keys. """
    return dict(zip(d.values(), d.keys()))

def capitolize(s:str) -> str:
    try:
        return s[0].upper() + s[1:]
    except IndexError:
        return s
