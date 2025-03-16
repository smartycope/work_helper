from collections import OrderedDict
from pathlib import Path

Documents = Path.home() / 'Documents'
LOG_PATH = Documents / 'helper_log.csv'
SAVE_CASE_PATH = Documents / 'Saved_Cases'
SAVE_NOTES_PATH = Documents / 'Case_Notes'
SAVE_STATE_PATH = Documents / 'helper_state.json'
INTERNAL_LOG_PATH = Documents / 'helper_log_internal.txt'
HINTS_PATH = Path(__file__).resolve().parent.parent / 'data' / 'hints.json'

for path in (SAVE_CASE_PATH, SAVE_CASE_PATH):
    path.mkdir(parents=True, exist_ok=True)

if not LOG_PATH.exists():
    with LOG_PATH.open('w') as f:
        f.write('action,id,color,serial,timestamp\n')

SIDEBAR_WIDTH = 30
COPY_SERIAL_BUTTON_WIDTH = 8
COLORS = OrderedDict((
    ("#377a11", "Green"),
    ("#ef9e16", "Orange"),
    ("#d1dd0b", "Yellow"),
    ("#ea9daf", "Pink"),
    ("#799fad", "Blue"),
))
DEFAULT_COLOR = '#9f9f9f'

EXISTING_CASES = {path.name.split('.')[0]: path for path in SAVE_CASE_PATH.iterdir()}

# Don't touch this, this gets set at the beginning of the program
DEBUG = None

# The phrase that puts you into debug mode
SECRET_PASSWORD = 'Cope is a genius'
# Password for SerialParser. Yes, this is horribly insecure. I'm aware.
# This isn't used anymore
PASSWORD = 'iHeartiRobot'

# SERIAL_PARSER_ICON = ':bookmark_tabs:'
SERIAL_PARSER_ICON = '📑'
PARSE_BBK_ICON = '📖'

# To avoid additional dependencies. My "Cope" package is horribly unstable
def invert_dict(d:dict) -> dict:
    """ Returns the dict given, but with the keys as values and the values as keys. """
    return dict(zip(d.values(), d.keys()))

# Yes, this is mispelled. I know. I don't feel like fixing it.
def capitolize(s:str) -> str:
    try:
        return s[0].upper() + s[1:]
    except IndexError:
        return s

# Same here
def uncapitolize(s:str) -> str:
    try:
        # Don't uncapitolize it if it's an acronym, or yourself. Names are out of luck
        if not s[1].isupper() and s[0:1] != 'i ':
            return s[0].lower() + s[1:]
        else:
            return s
    except IndexError:
        return s

# Thank you ChatGPT
def darken_color(hex_color, factor=0.7):
    """Darken a hex color by multiplying each channel by the given factor."""
    hex_color = hex_color.lstrip("#")  # Remove '#' if present
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    # Apply darkening factor and clamp values to 0-255
    r, g, b = [max(0, int(c * factor)) for c in (r, g, b)]

    return f"#{r:02x}{g:02x}{b:02x}"  # Convert back to hex format
