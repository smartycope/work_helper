
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

from RobotInfo import RobotInfo


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
        self.info.serials.clear()
        self.info.add_serial(to)
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
