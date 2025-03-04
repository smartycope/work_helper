
""" A minimal version of the main app that just parses the serial numbers """

import os
import traceback
from textual.app import App

from textual import on
from textual.containers import *
from textual.widgets import *

from ExternalNotesMenu import ExternalNotesMenu
from HintsMenu import HintsMenu

from globals import INTERNAL_LOG_PATH, PASSWORD

STARTING_TEXT = "Enter a model number, a serial number, or 2 serial numbers back to back. If 2 serial numbers are given, it will confirm that they're the same, and warn you if they're not."

# TODO: move this into it's own file
# TODO: incorperate this into Case (but remember that is_factory_lapis and is_weird_i5g have been changed)
# TODO: allow for multiple serials again
# TODO: finish moving sleep_mode and factory_reset into this class
class RobotInfo:
    """ The class that holds all the info relating to a robot (and later all the robots in a given case),
        gleaned from parsing the serial number[s].

        It knows nothing of docks, other than which docks the current robot can use

        Internally, all serial numbers are guarenteed lowercase, and then re-uppercased to the user.
        This is dumb, but it's how I did it at the beginning for some reason, and it would require a
        large rewrite to fix, so whatever. I'll get to it eventually.

        NOTE: going forward, this is the most up to date version, until I get around to merging this
        into Case.
    """

    ten_sec = 'Hold home for 10 seconds. Indicators should turn off'
    lift_wheel = 'Lift one wheel and hold clean for 3 seconds. Indicators should turn off'
    sleep_mode = {
        'i': ten_sec,
        's': ten_sec,
        'm': ten_sec,
        'j': lift_wheel,
        'c': lift_wheel,
        'e': 'Hold clean for 12 seconds. Release after the tone. Then, all indicators should turn off',
        'r': 'Add the plastic piece',
    }

    all_3 = 'Hold down all 3 buttons until the clean lights start to spin'
    remove_bin = 'Remove dust bin, then hold clean for 7 seconds until it beeps. Press clean again to confirm'
    factory_reset = {
        's': all_3,
        'i': all_3,
        'm': all_3,
        'j': remove_bin,
        'c': remove_bin,
        'e': 'Hold home and spot together for 20 seconds',
        'r': 'Hold dock and spot and clean until all LEDs turn on (9xx), or it beeps (6xx & 8xx)',
    }

    def __init__(self, serial=None):
        # We want the serial to evaluate to still false, but be a string
        self.serial = serial or ''

    def get_DCT(self) -> str:
        if self.serial.startswith('i') and not self.is_modular:
            return '[on red]Red card[/] from the top'
        elif self.serial.startswith(('i1', 'i2', 'i3', 'i4', 'i5')):
            return '[black on red]Red card[/]'
        elif self.serial.startswith('r') and not self.serial.startswith('r9'):
            return 'Serial'
        elif self.serial.startswith(('r', 's')):
            return 'USB'
        elif self.serial.startswith(('j8', 'q7', 'i6', 'i7', 'i8')):
            return '[black on green]Green card[/]'
        elif self.serial.startswith('m6'):
            return 'Small debug card, use Trident driver'
        elif self.serial.startswith(('j9')):
            return '[black on blue]Blue card[/]'
        elif self.serial.startswith('c9'):
            return '[black on green]Green card[/] through the pad'
        elif self.serial.startswith('c7'):
            return '[black on green]Green card[/] / [black on blue]Blue card[/] through the pad'
        elif self.serial.startswith('e'):
            return '[black on green]Green card[/], with micro USB\nplugged into the other side\non the card'
        elif self.serial.startswith(('j7', 'j5', 'j6')):
            return '[black on green]Green card[/] / [black on blue]Blue card[/]'
        else:
            return 'Error: Model from serial number not recognized'

    def get_DCT_exceptions(self) -> str:
        """ DCT known failures:
            J-Series robots with FW version 24.29.x will fail test #2 dock comms.
                ○ Ensure robot will evacuate and ignore DCT dock comms failure
            ● S9 robots may fail vacuum tests with low-current above 1000.
                ○ Ignore as long as value is below 1500
            ● Some robots will fail optical bin tests. 2 failures allowed, as long as the values are close
                ○ E.G. 500-1000 and the robot fails with 490.
            ● Pad detection tests on the M6 will sometimes fail.
                ○ Ignore if both wet and dry mobility missions are successful.
            ● C7 and C9 robots will fail actuator arm with FW's higher that 23.53.6
                ○ As long as the actuator arm will deploy normally during mobility and the failures
                    are for speed and range, ignore DCT.
            ● Battery charging will fail on a full battery
                ○ Ignore if you know the battery State of Charge is high.
        """
        if not self.is_modular:
            rtn = 'DCT won\'t work, only BBK'
        elif self.serial.startswith(('i3', 'i4', 'i5')):
            rtn = 'Any of the bumper tests can fail'
        elif self.serial.startswith('j9'):
            rtn = 'If v2 (clip battery), can fail basically everything. Otherwise, second dock comms test, if FW == 24.29.x (ensure robot still evacs)'
        elif self.serial.startswith('j'):
            rtn = 'Second dock comms test, if FW == 24.29.x (ensure robot still evacs)'
        elif self.serial.startswith('s9'):
            rtn = 'Low-current vacuum test, pass if the value is <1500'
        elif self.serial.startswith('m'):
            rtn = 'Pad detection test (run both wet and dry missions). If the sprayer on current is too low, charge and try again'
        elif self.serial.startswith('c'):
            rtn = 'Actuator arm current and speed tests, if FW >= 23.53.6 (ensure it deploys in mobility mission). If FW >= v24.29.5, DCT is brand new. FW >= v24.29.1: dock comms can fail'
            if self.serial.startswith('c9'):
                rtn = 'Sprayer current off, but note the firmware version. ' + rtn
        else:
            rtn = 'Optical bin tests (at most 2, if barely out of range)'

        if self.serial.startswith(('j7', 'j5', 'j6')):
            rtn += '\nIf uses the blue card, BiT may not work at all'

        return rtn

    def get_notes(self) -> str:
        notes = ''
        if self.serial.startswith('c9'):
            notes += "[on orange_red1]Remember to remove battery before removing the CHM.[/] Also, if the DCT card doesn't work, try a hard reset\nc955 -> Albany; c975 -> Aurora"

        # TODO: remove this once get_platform() works
        if self.serial.startswith('c'):
            if notes:
                notes += '\n'
            notes += 'CHM stingray: 4 wires, Pearl: 3 wires'

        if self.serial.startswith('i'):
            notes += 'If having weird trouble with DCT, try factory reset'

        if self.serial.startswith(('r', 'e')):
            # There's probably more models, but I don't know which ones
            home_is_next = not self.serial.startswith('r98')
            notes += f"To BiT: lights have to be off (hold down clean to turn off), then hold home & clean and press spot 5x. Then press {'home' if home_is_next else 'spot'} to start the tests. {'Spot is prev, home is next.' if home_is_next else 'Spot is next, home is prev.'} Hold clean when finished successfully, otherwise reset."

        if self.serial.startswith(('j7', 'j9')):
            notes += "If the blue DCT card doesn't work, try a hard reset"

        if self.has_weird_i5g:
            if notes:
                notes += '\n'
            notes += '[on orange_red1]Possibly a factory provisioned lapis bin[/]'

        elif self.is_factory_lapis:
            if notes:
                notes += '\n'
            notes += '[on red]Factory provisioned lapis bin![/]'

        return notes

    def get_platform(self) -> str:
        """ Unfinished, currently only works with combos, late J series models, and non-modular i series
            Returns an empty string if unknown
        """

        # the 6th digit from the end (the | in C755020B220912N|02026)
        # C7/J7: 0, 1, 2: Stingray (v1) | 3: Pearl (v2) | 4: Topaz (v3)
        # J9/C9: 0-3: Pearl max (v1) | 4: Topaz (v2)
        # C10: 4: Topaz (v1)
        if len(self.serial) < 17:
            # return "Unknown, need a full serial number"
            return ''
        digit = self.serial[-6]
        if self.serial.startswith(('c7', 'j7')):
            if digit in '012':
                return 'Stingray (v1)'
            elif digit == '3':
                return 'Pearl (v2)'
            elif digit == '4':
                return 'Topaz (v3)'
            else:
                return ''
        elif self.serial.startswith(('c9', 'j9')):
            if digit in '0123':
                return 'Pearl Max (v1)'
            elif digit == '4':
                return 'Topaz (v2)'
            else:
                return ''
        elif self.serial.startswith(('c10', 'j10', 'x')):
            if digit == '4':
                return 'Topaz (v1)'
            else:
                return ''
        elif self.serial.startswith('i') and not self.is_modular:
            return 'K2'
        else:
            return ''

    def get_docks(self) -> list[str]:
        """ Get a sorted list of the docks this model can use, the first element being the preferred one """

        camera = ['Albany', 'Zhuhai', 'Bombay']
        ir = ['Albany', 'Tianjin', 'Torino']

        if self.serial.startswith('m6'):
            return ['San Marino']
        elif self.serial.startswith('s9'):
            return ['Fresno']
        # C9's can use Boulders! Unknown if C7's can
        # elif self.serial.startswith('c9'):
            # return ['Aurora'] + camera
        elif self.serial.startswith(('c10', 'c9', 'x')):
            return ['Aurora', 'Boulder'] + camera
        elif self.serial.startswith('c7'):
            return camera + ['Aurora']
        elif self.serial.startswith(('j', 'c')):
            return camera
        else:
            return ir

    # TODO: make this not private
    def _ids_equal(self, a, b):
        """ Test if the ID's are equivelent
            i.e.
            i517020v230531n400186 ==
            i5g5020v230531n400186
        """
        if a.lower().startswith('i5') and len(a) > 3 and len(b) > 3:
            return a[:2] == b[:2] and a[4:] == b[4:]
        else:
            return a == b

    @property
    def can_mop(self):
        if self.serial:
            return self.serial.startswith(('m', 'c'))

    @property
    def can_vacuum(self) -> bool:
        if self.serial:
            return not self.serial.startswith('m')

    @property
    def is_combo(self):
        if self.serial:
            return self.serial.lower().startswith('c')

    # TODO: rename this to is_factory_lapis_case() or something more general
    @property
    def is_factory_lapis(self):
        """ True if *any* of the serials are a factory lapis, not just the current one """
        # if self.serial.startswith(('e', 'r')):
        #     return False
        try:
            # return any(i[3] == '7' for i in self.serials)
            return self.serial[3] == '7'
        except IndexError:
            return False

    @property
    def is_modular(self):
        if self.serial:
            if self.serial.startswith(('e', 'r')):
                return True

        # If the 8th digit of the serial number, if N or Z, indicates it's non-modular -- or if the 16th digit is 7, but focus on the first one
        if len(self.serial) > 7:
            return self.serial[7] not in ('n', 'z')
        else:
            # If not given all the info, assume it is
            return True

    @property
    def has_weird_i5g(self):
        if self.serial:
            return self.serial.startswith('i5g')

    def get_quick_model(self):
        if not self.serial:
            return ''
        elif self.serial[0] in ('r', 'k'):
            return self.serial[1:4]
        else:
            return self.serial[:2].upper()

    def statement(self):
        """ Return a nice looking summary of all the information to display to the user """
        # The web interface can't get the terminal size, and I'm too lazy to actually set up multiple
        # widgets with nice looking Rules in between them, so this works
        try:
            width = os.get_terminal_size().columns - 2
        except OSError:
            width = 50
        # Looks cleaner than dashes
        char = '─'
        platform = self.get_platform()
        return f"""
[bold]{self.get_quick_model()}[/] {('• ' + platform) if platform else ''}
[grey35]{self.serial.upper()}[/]

DCT: {self.get_DCT()}

{" DCT Exceptions ":{char}^{width}}
{self.get_DCT_exceptions()}

{" Shipping Mode ":{char}^{width}}
{self.sleep_mode.get(self.serial[0], 'Unknown')}

{" Factory Reset ":{char}^{width}}
{self.factory_reset.get(self.serial[0], 'Unknown')}

{" Notes ":{char}^{width}}
{self.get_notes()}
"""



class SerialParser(App):
    BINDINGS = [
        Binding('ctrl+e', 'toggle_external_notes_menu', 'External Notes', priority=True, system=True),
        Binding('ctrl+i', 'toggle_hints_menu', 'Hints', priority=True, system=True),
    ]

    CSS_PATH = "serial_parser_stylesheet.tcss"

    def __init__(self):
        super().__init__()
        self.password = PASSWORD
        self.password_input = Input(password=True, placeholder='Enter password', id='password_input')
        self.message = Label('', id='message')

        self.input = Input(placeholder='Input the model, one serial number, or 2 serial numbers', id='input')
        self.input.cursor_blink = False
        self.text = Label(STARTING_TEXT, id='label')
        self.info = RobotInfo()

        self.external_notes_menu = ExternalNotesMenu()
        self.hints_menu = HintsMenu(self)

    @property
    def serial(self):
        return self.info.serial

    # NO idea why this won't work
    # @serial.setter
    def set_serial(self, to):
        self.info.serial = to
        self.external_notes_menu.case = to
        self.text.update(self.info.statement())

    def compose(self):
        yield self.password_input
        yield self.message

        # This gets mounted once the password is authenticated
        self.contents = VerticalGroup(
            self.external_notes_menu,
            self.hints_menu,
            self.input,
            ScrollableContainer(self.text),
            Footer(),
        )

    def action_toggle_external_notes_menu(self):
        if self.serial:
            self.external_notes_menu.action_toggle()

    def action_toggle_hints_menu(self):
        if self.serial:
            self.hints_menu.action_toggle()

    # TODO: abstract this into a global function, so both Case and this can use it
    @on(Input.Submitted, '#input')
    def serial_submitted(self, event: Input.Submitted):
        try:
            if event.input.value:
                ids=  event.input.value.lower()
                # If they're different lengths, just assume they've inputted a single serial number
                # serial numbers are 21 characters long
                if len(ids) % 2 or len(ids) <= 25:
                    self.set_serial(ids)
                    event.input.clear()
                    return
                else:
                    half = len(ids)//2
                    if not self.info._ids_equal(ids[half:], ids[:half]):
                        self.text.update(f'\n\n!!! Serial numbers are different !!!\n{ids[half:]}\n{ids[:half]}')
                        event.input.clear()
                        return

                # self.serial = ids[len(event.input.value)//2:]
                self.set_serial(ids[len(event.input.value)//2:])

            event.input.clear()
        except:
            self.text.update(traceback.format_exc())

    def action_focus_input(self):
        self.input.focus()

    @on(Input.Submitted, '#password_input')
    def check_password(self, event: Input.Submitted):
        # If the correct password is given, remove the password box (and message), and mount the main app contents
        if event.input.value == self.password:
            self.message.update('Correct! Running app...')
            self.password_input.remove()
            self.message.remove()
            self.mount(self.contents)
            self.input.focus()
        else:
            self.message.update('Incorrect password. Please try again.')
            event.input.clear()
            self.password_input.focus()


if __name__ == "__main__":
    try:
        app = SerialParser()
        app.run()
    except:
        # Log the error if there is one
        with open(INTERNAL_LOG_PATH, 'a') as f:
            f.write(traceback.format_exc())
