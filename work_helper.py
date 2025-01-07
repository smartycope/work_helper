from collections import OrderedDict
import random
import re
import textwrap
from enum import Enum
from pathlib import Path

from clipboard import copy
from textual.app import App, ComposeResult
from textual.containers import *
from textual.document._document import Selection
from textual.reactive import reactive
from textual.widgets import *
import argparse

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

if args.debug:
    with open('~/Documents/deleteme_log.txt', 'w') as f:
        f.write('')

    _print = print
    def print(*a, **kw):
        with open('~/Documents/deleteme_log.txt', 'a') as log:
            _print(*a, file=log, **kw)

evac, visual, ir = 'evac', 'visual', 'ir'
docks = { #        is dock
    'Albany': (True, evac, visual, ir),
    'Aurora': (True, evac, visual, ir),
    'Bombay': (False, visual),
    'Boulder': (True, evac, visual, ir),
    'Fresno': (True, evac, ir),
    'San Marino': (False, ir),
    'Tianjin': (True, evac, ir),
    'Torino': (False, ir),
    'Zhuhai': (True, evac, visual),
}

ten_sec = 'Hold home for 10 seconds. Indicators should turn off'
lift_wheel = 'Lift one wheel and hold clean for 3 seconds. Indicators should turn off, then press clean again to confirm'
sleep_mode = {
    'i': ten_sec,
    's': ten_sec,
    'm': ten_sec,
    'j': lift_wheel,
    'c': lift_wheel,
    'e': 'Hold clean for 12 seconds. Release after the tone. Then, all indicators should turn off',
    'r': 'Add the plastic piece',
}

spot_and_clean = 'Hold down spot and clean together until the clean lights start to spin'
remove_bin = 'Remove dust bin, then hold clean for 7 seconds until it beeps. Press clean again to confirm'
factory_reset = {
    's': spot_and_clean,
    'i': spot_and_clean,
    'j': remove_bin,
    'c': remove_bin,
    'e': 'Hold home and spot together for 20 seconds',
    'r': 'Hold dock and spot and clean until all LEDs turn on (9xx), or it beeps (6xx & 8xx)',
    'm': 'Go ask',
}

class Phase(Enum):
    CONFIRM = 0
    ROUTINE_CHECKS = 1
    DEBUGGING = 2
    FINISH = 3

class Steps:
    manual_get_serial = 'Enter the model number, or scan a serial number'
    todo = 'TODO'

    confirm_id = 'Confirm IDs'
    check_repeat = 'Check if case is a repeat'
    check_spl_sku = 'Check that the SPL SKU is valid'
    pick_up_case = 'Go pick up the case on CSS (case ID copied)'
    ask_dock = 'Additional dock'
    ask_damage = 'Additional damage'
    customer_states = 'Customer States'
    check_liquid_damage = 'Signs of liquid damage [no]'
    ask_sunken_contacts = 'Sunken contacts [no]'
    ask_blower_play = 'Play in blower motor, or doesn\'t spin freely [no]'
    ask_rollers = 'Extractors are good [yes]'
    ask_s9_lid_pins = 'Are the lid pins sunken [no]'
    ask_cleaned = 'Robot cleaned ("na" if not, notes or empty if so)'
    battery_test = 'Battery test (don\'t forget the traveller) [current, health]'
    ask_user_base_contacts = 'Are the charging contacts on the user base good [yes]'
    ask_charge_customer_dock = "What's the charging wattage on the customer's dock"
    ask_charge_test_dock = "What's the charging wattage on a test base"
    ask_bin_rust = "Is there rust on the screw in the tank [no]"

    liquid_check_corrosion = 'Is there corrosion on the board or connections (specify or empty for no)'
    liquid_check_dock = 'Is there liquid residue in the user dock [no]'
    liquid_check_bin = 'Is there liquid residue in the robot bin [no]'
    liquid_take_pictures = 'Take pictures of liquid residue'

    sunken_ask_side = 'Which side is sunken (R/L)'
    sunken_ask_measurement = 'Contact measurement'

    add_step = 'Add Step'

class CustomTextArea(TextArea):
    # Modified from https://textual.textualize.io/widgets/text_area/#textual.widgets._text_area.TextArea.BINDINGS
    # TODO: most of these don't seem to work (anything with alt seems to get intercepted by Konsole)
    BINDINGS = [
        Binding("up,alt+k", "cursor_up", "Cursor up", show=False),
        Binding("down,alt+l", "cursor_down", "Cursor down", show=False),
        Binding("left,alt+j", "cursor_left", "Cursor left", show=False),
        Binding("right,alt+;", "cursor_right", "Cursor right", show=False),
        Binding("ctrl+left,ctrl+alt+j", "cursor_word_left", "Cursor word left", show=False),
        Binding("ctrl+right,ctrl+alt+;", "cursor_word_right", "Cursor word right", show=False),
        Binding("home,alt+h","cursor_line_start","Cursor line start",show=False),
        Binding("end,alt+'", "cursor_line_end", "Cursor line end", show=False),
        Binding("pageup", "cursor_page_up", "Cursor page up", show=False),
        Binding("pagedown", "cursor_page_down", "Cursor page down", show=False),
        Binding("ctrl+shift+left,ctrl+shift+alt+j", "cursor_word_left(True)", "Cursor left word select", show=False),
        Binding("ctrl+shift+right,ctrl+shift+alt+;", "cursor_word_right(True)", "Cursor right word select", show=False),
        Binding("shift+home,shfit+alt+h", "cursor_line_start(True)", "Cursor line start select", show=False),
        Binding("shift+end,shfit+alt+'", "cursor_line_end(True)", "Cursor line end select", show=False),
        Binding("shift+up,shift+alt+k", "cursor_up(True)", "Cursor up select", show=False),
        Binding("shift+down,shift+alt+l", "cursor_down(True)", "Cursor down select", show=False),
        Binding("shift+left,shift+alt+j", "cursor_left(True)", "Cursor left select", show=False),
        Binding("shift+right,shift+alt+;", "cursor_right(True)", "Cursor right select", show=False),
        Binding("ctrl+l", "select_line", "Select line", show=False),
        Binding("backspace", "delete_left", "Delete character left", show=False),
        Binding("ctrl+x", "cut", "Cut", show=False),
        Binding("ctrl+c", "copy", "Copy", show=True),
        Binding("ctrl+v", "paste", "Paste", show=False),
        # Binding("ctrl+u", "delete_to_start_of_line", "Delete to line start", show=False),
        # Binding("ctrl+k", "delete_to_end_of_line_or_delete_line", "Delete to line end", show=False),
        Binding("ctrl+shift+d", "delete_line", "Delete line", show=False),
        Binding("ctrl+z", "undo", "Undo", show=False),
        Binding("ctrl+y,ctrl+shift+z", "redo", "Redo", show=False),
        Binding('ctrl+a', 'select_all', 'Select All', show=False),
        Binding('esc', 'blur', 'Unfocus', show=False),
        Binding("ctrl+backspace", "delete_word_left", "Delete left to start of word", show=False),
        Binding("delete,shift+backspace", "delete_right", "Delete character right", show=False),
        Binding("ctrl+delete,ctrl+shift+backspace", "delete_word_right", "Delete right to start of word", show=False),
    ]

    def __init__(self, ref):
        super().__init__(ref + '\n', id='textarea_' + ref)
        self.cursor_blink = False

    def on_text_area_changed(self, event):
        # Always keep a single newline at the end of notes
        # Only run if there's multiple newlines at the end of the text (otherwise, infinte recursion)
        if re.match(r'(?:(?:.|\n))+(?:\s){2}\Z', self.text):
        # If there's *not* exactly one newline at the end of the text, then make sure there is one
        # This doesn't work, because it has to run while you're typing the middle of a word
        # if not re.match(r'(?:(?:.|\n))+(?:\S)+\n\Z', self.text):
            self.text = self.text.strip() + '\n'
            self.move_cursor(self.document.end, select=False)

class Sidebar(VerticalGroup):
    serial = reactive('')

    def __init__(self, case):
        super().__init__(id='sidebar-' + str(case.color))
        self.case = case

    def watch_serial(self, *args):
        if self.serial:
            self.model.update(f'{{:^{SIDEBAR_WIDTH}}}'.format(self.case.get_quick_model() + '\n'))
            self.sleep_mode.update(textwrap.fill(sleep_mode.get(self.serial[0], 'Unknown'), SIDEBAR_WIDTH) + '\n')
            self.factory_reset.update(textwrap.fill(factory_reset.get(self.serial[0], 'Unknown'), SIDEBAR_WIDTH) + '\n')
            self.dct.update(f'{{:^{SIDEBAR_WIDTH}}}'.format(textwrap.fill(self.case.get_DCT(), SIDEBAR_WIDTH)) + '\n')
            self.dct_exp.update(f'{{:^{SIDEBAR_WIDTH}}}'.format(textwrap.fill(self.case.get_DCT_exceptions(), SIDEBAR_WIDTH)) + '\n')
            self.serial_label.update(f'\n{self.serial.upper():^{SIDEBAR_WIDTH-COPY_SERIAL_BUTTON_WIDTH}}')
            # self.serial_label.update(self.serial)
            notes = textwrap.fill(self.case.get_notes(), SIDEBAR_WIDTH)
            if notes:
                self.notes_sep.update(f'{" Notes ":-^{SIDEBAR_WIDTH}}')
                self.notes.update(notes)

    def compose(self):
        self.color_switcher = Select(
            [(f'[{color}]{name}[/]', color) for color, name in COLORS.items()],
            id="color-selector",
            allow_blank=False,
            value=list(COLORS.keys())[self.case.color],
        )
        # self.color_switcher.styles.margin = 0
        # self.color_switcher.styles.padding = 0
        # self.color_switcher.styles.height = 1
        # self.color_switcher.styles.background = list(COLORS.keys())[self.case.color]
        self.color_switcher.can_focus = False
        yield self.color_switcher

        yield Label(f'{self.case.ref:^{SIDEBAR_WIDTH}}\n', id=f'ref-label-{self.case.color}')
        with HorizontalGroup():
            # yield Label(f'{"Phase":^{SIDEBAR_WIDTH}}\n')
            yield Label("\nPhase: ")
            s = Select([(i.name, i.value) for i in Phase], id='phase-select', allow_blank=False)
            s.can_focus = False
            yield s
        yield Label('\n')
        yield Label(f'{" Model ":-^{SIDEBAR_WIDTH}}')
        self.model = Label('', id=f'model-label-{self.case.color}')
        yield self.model
        yield Label(f'{" Sleep Mode ":-^{SIDEBAR_WIDTH}}')
        self.sleep_mode = Label('', id=f'sleep-mode-label-{self.case.color}')
        yield self.sleep_mode
        yield Label(f'{" Factory Reset ":-^{SIDEBAR_WIDTH}}')
        self.factory_reset = Label('', id=f'factory-reset-label-{self.case.color}')
        yield self.factory_reset
        yield Label(f'{" DCT ":-^{SIDEBAR_WIDTH}}')
        self.dct = Label('', id=f'dct-label-{self.case.color}')
        yield self.dct
        yield Label(f'{" DCT Exceptions ":-^{SIDEBAR_WIDTH}}')
        self.dct_exp = Label('', id=f'dct-exp-label-{self.case.color}')
        yield self.dct_exp
        self.notes_sep = Label('')
        yield self.notes_sep
        self.notes = Label('', id=f'notes-label-{self.case.color}')
        yield self.notes

        with VerticalGroup(id='lower-sidebar'):
            yield Label('TODO:')
            ta = TextArea(id='todo-textarea')
            yield ta
            yield Label('')

            self.serial_label = Label(' '*(SIDEBAR_WIDTH-COPY_SERIAL_BUTTON_WIDTH), id=f'serial-label-{self.case.color}')
            self.id_button = Button(f'Copy', id='copy-serial-button')
            self.id_button.can_focus = False
            with HorizontalGroup():
                yield self.serial_label
                yield self.id_button

            yield Label('')
            button = Button('Copy Notes', id='copy-button')
            button.can_focus = False
            yield button

    def on_button_pressed(self, event):
        match event.button.id:
            case 'copy-button':
                copy(self.case.text_area.text.strip())
            case 'copy-serial-button':
                copy(self.serial)

class Case(VerticalGroup):
    step = reactive(Steps.confirm_id)
    phase = reactive(Phase.CONFIRM)

    def __init__(self, id, color):
        super().__init__(id='case_'+str(color))
        self.ref = id
        self.serial = None
        self.dock = None
        self.color: int = color
        self.customer_states = None

        self.prev_step = None

        self._liquid_swap = None
        self._sunken_side = None

        self.text_area = CustomTextArea(self.ref)

        self.input = Input(placeholder=self.step, id='input_' + self.ref)
        self.input.cursor_blink = False
        self.sidebar = Sidebar(self)
        # other_colors = COLORS.copy()
        # other_colors.pop(list(other_colors.keys())[color])

    def change_color(self, to_color):
        old_color = self.color
        if old_color != to_color:
            self.color = to_color
            hex = list(COLORS.keys())[to_color]
            # self.id = 'case_'+str(to_color)
            # self.sidebar = Sidebar(self)
            # self.sidebar.serial = self.serial
            self.sidebar.styles.background = hex
            self.parent.parent.parent.get_tab(self.parent.id).styles.background = hex
            # self.refresh()
            # self.update()


    def compose(self):
        yield self.text_area
        yield self.input
        yield self.sidebar

        self.input.focus()

    def watch_step(self, to):
        # Because as a reactive attribute, it apparently runs before mounting (before compose is called)
        try:
            self.prev_step = self.step
            self.input.placeholder = to
        except:
            pass

    def watch_phase(self, to):
        # No idea why I need to cast it to Phase here
        self.query_one('#phase-select').value = Phase(to).value

    def add_step(self, step, bullet='*'):
        self.text_area.text += f'{bullet} {step}\n'

    def on_select_changed(self, event: Select.Changed) -> None:
        match event.select.id:
            case "color-selector":
                self.change_color(list(COLORS.keys()).index(event.value))
            case "phase-select":
                self.phase = Phase(event.value)
                match self.phase:
                    case Phase.CONFIRM:
                        self.step = Steps.confirm_id if not self.serial else Steps.check_repeat
                    case Phase.ROUTINE_CHECKS:
                        self.ensure_serial(Steps.check_liquid_damage)
                    case Phase.DEBUGGING:
                        self.ensure_serial(Steps.add_step)
                    # TODO
                    case Phase.FINISH:
                        self.ensure_serial(Steps.todo)

    def ensure_serial(self, next_step):
        """ If we don't have a serial number, ask for one manually, then go back to what we were
            doing. If we do have a serial number, just continue"""
        if not self.serial:
            self.step = Steps.manual_get_serial
            self._step_after_manual_serial = next_step
        else:
            self.step = next_step

    # The main algorithm is here
    def on_input_submitted(self):
        resp = self.input.value
        self.input.value = ''
        # To simplify some of the redundant next step logic
        next_step = None

        # TODO: I think back isn't working
        if resp.lower() == 'back' and self.step != Steps.confirm_id:
            self.step = self.prev_step
            return

        if self.step == Steps.manual_get_serial:
            if resp:
                self.serial = resp.lower()
                self.sidebar.serial = self.serial.lower()
                self.step = self._step_after_manual_serial
            return

        if self.phase == Phase.CONFIRM:
            match self.step:
                # Main path
                case Steps.confirm_id:
                    # If we (somehow) already have the serial number, we don't need to confirm it
                    if self.serial:
                        self.step = Steps.check_repeat
                        return

                    ids=  resp.lower()
                    if not resp:
                        # If they don't put anything, assume we aren't comparing serial numbers, and we just want to input one
                        self.ensure_serial(Steps.check_repeat)
                        return
                    else:
                        if len(ids) % 2:
                            self.text_area.text = self.step = '!!! Serial numbers are different lengths !!!'
                            return
                        else:
                            half = len(ids)//2
                            if ids[half:] != ids[:half]:
                                self.text_area.text = self.step = '!!! Serial numbers are different !!!'
                                return
                        self.serial = ids[len(resp)//2:].lower()
                        # Fill in all the info now that we have the serial number
                        self.sidebar.serial = self.serial
                        self.step = Steps.check_repeat

                case Steps.check_repeat:
                    self.step = Steps.check_spl_sku

                case Steps.check_spl_sku:
                    copy(self.ref)
                    self.step = Steps.pick_up_case

                case Steps.pick_up_case:
                    self.step = Steps.ask_dock

                case Steps.ask_dock:
                    self.dock = resp
                    self.text_area.text += 'Parts in: Robot'
                    if resp:
                        self.text_area.text += ', ' + resp + ', cord'
                    self.text_area.text += '\n'
                    self.step = Steps.ask_damage

                case Steps.ask_damage:
                    self.text_area.text += 'Claimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage'
                    if resp:
                        self.text_area.text += ', ' + resp[0].lower() + resp[1:]
                    self.text_area.text += '\n'
                    self.step = Steps.customer_states

                case Steps.customer_states:
                    if resp:
                        self.customer_states = resp[0].upper() + resp[1:]
                        self.text_area.text += 'Customer States: ' + self.customer_states + '\n\nRoutine Checks:\n'
                        self.step = Steps.check_liquid_damage
                        self.phase = Phase.ROUTINE_CHECKS

        elif self.phase == Phase.ROUTINE_CHECKS:
            match self.step:
                case Steps.check_liquid_damage:
                    if resp.lower() == 'na':
                        self.step = Steps.ask_sunken_contacts
                    elif resp:
                        self.add_step('Found signs of liquid residue', bullet='!')
                        self.step = Steps.liquid_check_corrosion
                    else:
                        self.add_step('No signs of liquid damage')
                        self.step = Steps.ask_sunken_contacts

                case Steps.ask_sunken_contacts:
                    if resp.lower() == 'na':
                        self.step = Steps.ask_blower_play
                    elif resp:
                        self.step = Steps.sunken_ask_side
                    else:
                        self.add_step('Contacts don\'t feel sunken')
                        self.step = Steps.ask_blower_play

                case Steps.ask_blower_play:
                    if resp.lower() != 'na':
                        if resp:
                            self.add_step('Found play in the blower motor', bullet='!')
                        else:
                            self.add_step('No play in blower motor')
                    self.step = Steps.ask_rollers

                case Steps.ask_rollers:
                    if resp and resp.lower() != 'na':
                        self.add_step('Extractors are bad', bullet='!')

                    if self.serial.lower().startswith('c'):
                        self.step = Steps.ask_bin_rust
                    else:
                        next_step = 'cleaning/lid pins'

                case Steps.ask_bin_rust:
                    if resp:
                        self.add_step('Tank float screw has rust on it', bullet='!')
                    else:
                        self.add_step('Tank float screw has no signs of rust')

                    next_step = 'cleaning/lid pins'

                # TODO: extend this in the future to go into swap
                case Steps.ask_s9_lid_pins:
                    if resp:
                        self.add_step('Lid pins are sunken', bullet='!')
                    self.step = Steps.ask_cleaned

                case Steps.ask_cleaned:
                    if resp.lower() != 'na':
                        self.add_step('Cleaned robot' + ((' - ' + resp) if resp else ''))

                    if self.dock:
                        self.step = Steps.ask_user_base_contacts
                    else:
                        next_step = 'battery_test/charging'

                case Steps.ask_user_base_contacts:
                    if resp.lower() != 'na':
                        self.add_step(f"Charging contacts on the customer's {self.dock} look {'bad' if resp else 'good'}", bullet='!' if resp else '*')

                    next_step = 'battery_test/charging'

                case Steps.battery_test:
                    if resp.lower() != 'na':
                        charge, health = resp.split(',')
                        self.add_step(f'Tested battery: {charge.strip()}%/{health.strip()}%', bullet='!' if float(health.strip()) < 80 else '*')

                    next_step = 'charging'

                case Steps.ask_charge_customer_dock | Steps.ask_charge_test_dock:
                    if resp.lower() != 'na':
                        try:
                            watts = round(float(resp))
                        except ValueError:
                            if resp:
                                self.add_step(resp)
                                self.step = Steps.add_step
                                self.phase = Phase.DEBUGGING
                            return

                        dock = f'customer {self.dock}' if self.dock else 'test base'

                        if watts < 3:
                            self.add_step(f"Robot does not charge on {dock} @ ~{watts}W", bullet='!')
                        elif watts < 10:
                            self.add_step(f"Robot charges on {dock} @ ~{watts}W (battery is full)")
                        else:
                            self.add_step(f"Robot charges on {dock} @ ~{watts}W")

                    self.step = Steps.add_step
                    self.phase = Phase.DEBUGGING

                # Liquid damage path
                case Steps.liquid_check_corrosion:
                    if resp.lower() != 'na':
                        if resp:
                            self.add_step(f'Found signs of liquid corrosion on the {resp}', bullet='**')
                            self._liquid_swap = True
                        else:
                            self.add_step('No signs of liquid damage on the main board or connections', bullet='**')

                    next_step = 'liquid check dock or bin'

                case Steps.liquid_check_dock:
                    if resp.lower() != 'na':
                        if resp:
                            self.add_step(f'Liquid residue found in the user {self.dock}', bullet='**')
                        else:
                            self.add_step(f'No signs of liquid residue found in the user {self.dock}', bullet='**')
                    self.step = Steps.liquid_check_bin

                case Steps.liquid_check_bin:
                    if resp.lower() != 'na':
                        if resp:
                            self.add_step('Liquid residue found in customer bin: probably sucked up liquid', bullet='**')
                        else:
                            self.add_step('No liquid residue found in customer bin', bullet='**')
                    self.step = Steps.liquid_take_pictures

                # TODO connect to finish phase
                case Steps.liquid_take_pictures:
                    if self._liquid_swap:
                        self.add_step('Diagnosis: Liquid damage', bullet='-')
                        self.add_step('Swap robot')
                        # self.phase = Phase.FINISH
                        self.step = Steps.add_step
                        self.phase = Phase.DEBUGGING
                    else:
                        # If there's liquid residue, but not on the main board, proceed
                        self.step = Steps.ask_sunken_contacts

                # Sunken contacts path
                case Steps.sunken_ask_side:
                    self._sunken_side = 'right' if resp.lower() == 'r' else 'left'
                    self.step = Steps.sunken_ask_measurement

                # TODO connect to finish phase
                case Steps.sunken_ask_measurement:
                    try:
                        measurement = float(resp)
                    except ValueError:
                        # Don't change the step, try again until we get a float
                        return

                    self.add_step(f'Measured {self._sunken_side} contact: {resp}mm +/- .1')

                    if measurement < 3.8:
                        self.add_step(f'Diagnosis: Sunken {self._sunken_side} contact', bullet='-')
                        self.add_step('Swap robot' + (f' and customer {self.dock}' if self.dock else ''))
                        self.step = Steps.add_step
                        self.phase = Phase.FINISH

                    self.step = Steps.ask_blower_play

        elif self.phase == Phase.DEBUGGING:
            match self.step:
                case Steps.add_step:
                    if resp:
                        if 'Process:' not in self.text_area.text:
                            self.text_area.text += '\nProcess:\n'
                        self.add_step(resp[0].upper() + resp[1:])

        # TODO
        elif self.phase == Phase.FINISH:
            match self.step:
                case _:
                    pass

        # To simplify repeated next step logic
        match next_step:
            case 'battery_test/charging':
                if 'charg' in self.customer_states.lower() and self.dock:
                    self.step = Steps.battery_test
                else:
                    self.step = Steps.ask_charge_customer_dock if self.dock else Steps.ask_charge_test_dock
            case 'charging':
                self.step = Steps.ask_charge_customer_dock if self.dock else Steps.ask_charge_test_dock
            case 'liquid check dock or bin':
                self.step = Steps.liquid_check_dock if self.dock else Steps.liquid_check_bin
            case 'cleaning/lid pins':
                if self.serial.lower().startswith('s'):
                    self.step = Steps.ask_s9_lid_pins
                else:
                    self.step = Steps.ask_cleaned

        self.text_area.scroll_to(None, 1000, animate=False)

    # Helper methods
    def get_quick_model(self):
        if self.serial[0] == 'r':
            return self.serial[1:4]
        else:
            return self.serial[:2].upper()

    def get_DCT(self):
        if self.serial.startswith(('i1', 'i2', 'i3', 'i4', 'i5')):
            return 'Red card'
        elif self.serial.startswith('r') and not self.serial.startswith('r9'):
            return 'Serial'
        elif self.serial.startswith(('r', 's')):
            return 'USB'
        elif self.serial.startswith(('j8', 'q7', 'i6', 'i7', 'i8', 'c9')):
            return 'Green card'
        elif self.serial.startswith('m6'):
            return 'Small debug card, use Trident driver'
        elif self.serial.startswith(('j9')):
            return 'Blue card'
        elif self.serial.startswith('e'):
            return 'Green card with micro USB plugged into right side'
        elif self.serial.startswith(('j7', 'c7')):
            return 'Green or Blue card. Try the Green card first'
        else:
            return 'Error: Model from serial number not recognized'

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

        if self.serial.startswith('j'):
            return 'Second dock comms test, if FW == 24.29.x (ensure robot still evacs)'
        elif self.serial.startswith('s9'):
            return 'Low-current vacuum test, pass if the value is <1500'
        elif self.serial.startswith('m'):
            return 'Pad detection test (run both wet and dry missions)'
        elif self.serial.startswith('c'):
            return 'Actuator arm test, if FW >= 23.53.6 (ensure it deploys in mobility mission)'
        else:
            return 'Optical bin tests (at most 2, if barely out of range)'

    def get_notes(self):
        if self.serial.startswith('j'):
            return 'If the last digit of the SPL SKU is 7, they have a Lapis bin at home! If the middle number is 1, it came with just a home base. In that case, don\'t test on a dock! Just a base.'
        return ''


if args.debug:
    ex1, ex2, ex3 = Case('12345IR', 1), Case('11111IR', 2), Case('54321IR', 3)
    ex1.serial = 'S9999'
    ex2.serial = 'C9123'
    ex3.serial = 'J7321'
    ex1.dock = 'Zhuhai'
    ex2.dock = ''
    ex3.dock = 'Torino'
    ex1.customer_states = 'charging issues'
    ex2.customer_states = 'it sucks'
    ex3.customer_states = 'no movement'
    ex1.color = 1
    ex2.color = 2
    ex3.color = 3

class HelperApp(App):
    BINDINGS = [
        ("n,ctrl+n", "new_case", "New Case"),
        ("ctrl+f", "close_case", "Close Case"),
        ("s,ctrl+s", "save", "Save"),
        ("__", "remove_double_lines", "Remove Double Lines"),
        # Binding('ctrl+tab', 'next_tab', 'Next Tab', show=True, priority=True),
        # Binding('ctrl+shift+tab', 'prev_tab', 'Previous Tab', show=True, priority=True),
    ]
    CSS = '''
        TabbedContent #--content-tab-pane-0 {
            background: [color_0];
            color: black;
        }
        TabbedContent #--content-tab-pane-1 {
            background: [color_1];
            color: black;
        }
        TabbedContent #--content-tab-pane-2 {
            background: [color_2];
            color: black;
        }
        TabbedContent #--content-tab-pane-3 {
            background: [color_3];
            color: black;
        }
        TabbedContent #--content-tab-pane-4 {
            background: [color_4];
            color: black;
        }

        #sidebar-0 {
            dock: right;
            height: 100%;
            width: [SIDEBAR_WIDTH];
            background: [color_0];
            color: black;
        }
        #sidebar-1 {
            dock: right;
            height: 100%;
            width: [SIDEBAR_WIDTH];
            background: [color_1];
            color: black;
        }
        #sidebar-2 {
            dock: right;
            height: 100%;
            width: [SIDEBAR_WIDTH];
            background: [color_2];
            color: black;
        }
        #sidebar-3 {
            dock: right;
            height: 100%;
            width: [SIDEBAR_WIDTH];
            background: [color_3];
            color: black;
        }
        #sidebar-4 {
            dock: right;
            height: 100%;
            width: [SIDEBAR_WIDTH];
            background: [color_4];
            color: black;
        }

        #reference_popup {
            layer: above;
            content-align: center middle;
            align: center middle;
            width: 100%;
        }

        #copy-button{
            height: 3;
            width: 100%;
            dock: bottom;
        }

        #lower-sidebar{
            height: 25%;
            dock: bottom;
        }

        #todo-textarea{
            min-height: 5;
        }

        #copy-serial-button{
            width: [COPY_SERIAL_BUTTON_WIDTH];
            min-width: [COPY_SERIAL_BUTTON_WIDTH];
        }
    '''.replace('{', '{{').replace('}', '}}').replace('[', '{').replace(']', '}').format(
            SIDEBAR_WIDTH=SIDEBAR_WIDTH,
            COPY_SERIAL_BUTTON_WIDTH=COPY_SERIAL_BUTTON_WIDTH,
            color_0=list(COLORS.keys())[0],
            color_1=list(COLORS.keys())[1],
            color_2=list(COLORS.keys())[2],
            color_3=list(COLORS.keys())[3],
            color_4=list(COLORS.keys())[4],
        )

    def __init__(self, debug=False):
        super().__init__()
        self._debug = debug
        self.cases = []
        self.dir = Path.home() / 'Documents' / 'Case_Notes'
        self.dir.mkdir(parents=True, exist_ok=True)

        self.tabs = TabbedContent(id='tabs')
        self.popup = Input(placeholder='Case ID', id='reference_popup')
        self.popup.visible = False

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        if self._debug:
            with self.tabs:
                for i in range(3):
                    ref = f'1900{i}IR'
                    case = Case(ref, i)
                    self.cases.append(case)
                    yield TabPane(ref, case, id='pane-'+str(i))
        else:
            yield self.tabs
        yield self.popup
        yield Footer()

    def on_input_submitted(self):
        # This should be the only way cases get deployed
        if self.popup.visible:
            self.popup.visible = False
            ref = self.popup.value
            self.popup.value = ''
            if len(self.cases) < 5:
                unused_color = random.choice(list(set(range(5)) - {i.color for i in self.cases}))
                # If we can't create a case (like, if there's a space in the ID somehow or something), just don't make one
                try:
                    case = Case(ref, unused_color)
                except:
                    return
                self.cases.append(case)
                self.tabs.add_pane(TabPane(ref, case, id='pane-'+str(unused_color)))

    def action_new_case(self):
        """Add a new tab."""
        self.popup.visible = True
        self.popup.focus()

    def action_close_case(self):
        self.action_save()
        # Only close the case if we're in the final phase
        if self.active_case.phase == Phase.FINISH:
            self.cases.remove(self.active_case)
            self.tabs.remove_pane(self.tabs.active_pane.id)

    @property
    def active_case(self):
        return self.tabs.active_pane.children[0]

    def action_remove(self) -> None:
        """Remove active tab."""
        active_tab = tabs.active_tab
        if active_tab is not None:
            self.action_save()
            self.cases.remove(self.active_case)
            self.tabs.remove_tab(active_tab.id)

    def next_tab(self):
        # print('next tab called')
        # print(f'active case:', self.active_case.ref)
        idx = self.cases.index(self.active_case)
        next = self.cases[(idx+1)%len(self.cases)]
        print(f'next case:', next.ref)
        self.tabs.active = f'pane-{next.color}'

    def prev_tab(self):
        # print('prev tab called')
        idx = self.cases.index(self.active_case)
        prev = self.cases[idx-1]
        self.tabs.active = f'pane-{prev.color}'

    def action_save(self):
        for case in self.cases:
            with open(self.dir / (case.ref + '.txt'), 'w') as f:
                print('Saved cases to ', self.dir)
                f.write(case.text_area.text)

    def action_remove_double_lines(self):
        self.active_case.text_area.text = self.active_case.text_area.text.replace('\n\n', '\n')

if __name__ == "__main__":
    app = HelperApp(debug=args.debug)
    try:
        app.run()
    finally:
        app.action_save()

    if args.debug:
        with open('~/Documents/deleteme_log.txt') as f:
            _print(f.read())
