from collections import OrderedDict
from pathlib import Path

SIDEBAR_WIDTH = 30
COPY_SERIAL_BUTTON_WIDTH = 8
LOG_PATH = Path.home() / 'Documents' / 'helper_log.csv'
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
