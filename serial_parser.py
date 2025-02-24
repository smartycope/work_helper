""" A minimal version of the main app that just parses the serial numbers """

from textual.app import App

import json
from numpy import mean, std
import random
import re
from datetime import datetime
from difflib import get_close_matches
from typing import Union

from textual import on
from textual.containers import *
from textual.reactive import reactive
from textual.widgets import *

from ExternalNotesMenu import ExternalNotesMenu
from HintsMenu import HintsMenu

from info import DOCKS

STARTING_TEXT = 'TODO'

# TODO: incorperate this into Case (but remember that is_factory_lapis and is_weird_i5g have been changed)
class RobotInfo:
    def __init__(self, serial=None):
        self.serial = serial or ''

    def get_DCT(self):
        if self.serial.startswith('i') and not self.is_modular:
            return '[on red]Red card[/] from the top'
        elif self.serial.startswith(('i1', 'i2', 'i3', 'i4', 'i5')):
            return '[on red]Red card[/]'
        elif self.serial.startswith('r') and not self.serial.startswith('r9'):
            return 'Serial'
        elif self.serial.startswith(('r', 's')):
            return 'USB'
        elif self.serial.startswith(('j8', 'q7', 'i6', 'i7', 'i8')):
            return '[on green]Green card[/]'
        elif self.serial.startswith('m6'):
            return 'Small debug card, use Trident driver'
        elif self.serial.startswith(('j9')):
            return '[on blue]Blue card[/]'
        elif self.serial.startswith('c9'):
            return '[on green]Green card[/] through the pad'
        elif self.serial.startswith('c7'):
            return '[on green]Green card[/] / [on blue]Blue card[/] through the pad'
        elif self.serial.startswith('e'):
            return '[on green]Green card[/], with micro USB\nplugged into the other side\non the card'
        elif self.serial.startswith(('j7', 'j5', 'j6')):
            return '[on green]Green card[/] / [on blue]Blue card[/]'
        else:
            return 'Error: Model from serial number not recognized'
            # MINOR: in combo models, for the DCT card, remind to put it under the pad

    def get_DCT_exceptions(self):
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

        # URGENT: add DCT exception: if v2 J7 (uses blue card), DCT doesn't work (for now) for j series bots that use the green/blue card DCT, add DCT exceptions that it can fail entirely (for now)
        if self.serial.startswith(('j7', 'j5', 'j6')):
            rtn += '\nIf uses the blue card, BiT doesn\'t work at all'

        return rtn

    def get_notes(self):
        # if self.serial.startswith('j'):
            # return 'If the last digit of the SPL SKU is 7, they have a Lapis bin at home! If the middle number is 1, it came with just a home base. In that case, don\'t test on a dock! Just a base.'
        notes = ''
        if self.serial.startswith('c9'):
            notes += "[on orange_red1]Remember to remove battery before removing the CHM.[/] Also, if the DCT card doesn't work, try a hard reset\nc955 -> albany; c975 -> aurora"

        if self.serial.startswith('c'):
            notes += '\nCHM stingray: 4 wires, Pearl: 3 wires'

        if self.serial.startswith('i'):
            notes += 'If having weird trouble with DCT, try factory reset'

        if self.serial.startswith(('r', 'e')):
            # R989
            if self.serial.startswith('r98'):
                buttons = 'Spot is next, home is prev.'
            else:
                buttons = 'Spot is prev, home is next.'
            notes += f'To BiT: lights have to be off (hold down clean to turn off), then hold home & clean and press spot 5x. Then press home to start the tests. {buttons} Hold clean when finished successfully, otherwise reset.'

        # if self.serial.startswith('e'):
        #     notes += 'To BiT: lights have to be off, then hold home & clean and press spot 5x. You also have to press clean to get it to connect to DCT'

        if self.serial.startswith(('j7', 'j9')):
            notes += "If the blue DCT card doesn't work, try a hard reset"

        if self.has_weird_i5g:
            notes += '\n [on orange_red1]Possibly a factory provisioned lapis bin[/]'
        elif self.is_factory_lapis:
            notes += '\n [on red]Factory provisioned lapis bin![/]'

        return notes

    def get_docks(self):
        """ Get a sorted list of the docks this model can use, the first element being the preferred one """

        camera = ['Albany', 'Zhuhai', 'Bombay']
        ir = ['Albany', 'Tianjin', 'Torino']

        if self.serial.startswith('m6'):
            return ['San Marino']
        elif self.serial.startswith('s9'):
            return ['Fresno']
        # elif self.serial.startswith('c9'):
            # return ['Aurora'] + camera
        elif self.serial.startswith(('c10', 'c9', 'x')):
            return ['Boulder', 'Aurora'] + camera
        elif self.serial.startswith(('j', 'c')):
            return camera
        else:
            return ir

    def _ids_equal(self, a, b):
        """ i517020v230531n400186 ==
            i5g5020v230531n400186
        """
        if a.lower().startswith('i5') and len(a) > 3 and len(b) > 3:
            return a[:2] == b[:2] and a[4:] == b[4:]
        else:
            return a == b

    @property
    def can_mop(self):
        return self.serial.startswith(('m', 'c'))

    @property
    def can_vacuum(self) -> bool:
        return not self.serial.startswith('m')

    @property
    def is_combo(self):
        if self.serial:
            return self.serial.lower().startswith('c')
        else:
            return None

    @property
    def is_factory_lapis(self):
        """ True if *any* of the serials are a factory lapis, not just the current one """
        # if self.serial.startswith(('e', 'r')):
        #     return False
        # try:
        #     return any(i[3] == '7' for i in self.serials)
        # except IndexError:
        #     return False
        return self.serial[3] == '7'


    @property
    def is_modular(self):
        if self.serial.startswith(('e', 'r')):
            return True

        # If the 8th digit of the serial number, if N or Z, indicates it's non-modular -- or if the 16th digit is 7, but focus on the first one
        if len(self.serial) > 7:
            return self.serial[7] not in ('n', 'z')
        else:
            return True

    @property
    def has_weird_i5g(self):
        return self.serial.startswith('i5g')

    def get_quick_model(self):
        if not self.serial:
            return ''
        elif self.serial[0] == 'r':
            return self.serial[1:4]
        else:
            return self.serial[:2].upper()


    def statement(self):
        return 'stuuff'




class SerialParser(App):
    BINDINGS = [
        ('ctrl+e', 'toggle_external_notes_menu', 'External Notes'),
        ('ctrl+i', 'toggle_hints_menu', 'Hints'),
    ]

    CSS_PATH = "serial_parser_stylesheet.tcss"

    def __init__(self):
        super().__init__()
        self.input = Input(placeholder='Input the model, one, or both serials squished together', id='input')
        self.input.cursor_blink = False
        self.text_area = Label(STARTING_TEXT, id='label')
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
        self.text_area.update(self.info.statement())

    def compose(self):
        yield self.external_notes_menu
        yield self.hints_menu
        yield self.input
        yield Footer()

        self.input.focus()

    def action_toggle_external_notes_menu(self):
        if self.serial:
            self.external_notes_menu.action_toggle()

    def action_toggle_hints_menu(self):
        if self.serial:
            self.hints_menu.action_toggle()

    @on(Input.Submitted, '#input')
    def serial_submitted(self, event: Input.Submitted):
        if event.input.value:
            ids=  event.input.value.lower()
            # If they're different lengths, just assume they've inputted a single serial number
            # serial numbers are 21 characters long
            if len(ids) % 2 or len(ids) <= 25:
                # self.text_area.update('\n\n!!! Serial numbers are different lengths !!!')
                # self.serial = ids
                self.set_serial(ids)
                return
            else:
                half = len(ids)//2
                if not self.info._ids_equal(ids[half:], ids[:half]):
                    self.text_area.update(f'\n\n!!! Serial numbers are different !!!\n{ids[half:]}\n{ids[:half]}')
                    return

            # self.serial = ids[len(event.input.value)//2:]
            self.set_serial(ids[len(event.input.value)//2:])

    def action_focus_input(self):
        self.input.focus()


if __name__ == "__main__":
    app = SerialParser()
    app.run()
