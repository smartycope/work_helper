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

from AcronymMenu import AcronymMenu
from CommandsMenu import CommandsMenu
from CustomTextArea import CustomTextArea
from ExternalNotesMenu import ExternalNotesMenu
# from MenuMenu import MenuMenu
from globals import (COLORS, EXISTING_CASES, LOG_PATH, SAVE_CASE_PATH, SAVE_NOTES_PATH,
                     capitolize, darken_color, invert_dict)
from HintsMenu import HintsMenu
from info import DOCKS
from MobilityMenu import MobilityMenu
from Phase import Phase
from Sidebar import Sidebar
import settings
from texts import Steps


class Case(VerticalGroup):
    from parse_commands import parse_command
    from step_algorithm import (  # before_ask_copy_notes_1,
        after_ask_complete_case_CSS, after_generate_external_notes,
        _copy_swap_serial,
        after_pick_up_case, before_ask_complete_case_CSS,
        before_ask_copy_notes_2, before_ask_double_check,
        before_ask_submit_adj, before_generate_external_notes,
        before_hold_add_context, before_hold_copy_notes_to_CSS,
        before_pick_up_case, before_swap_email, before_swap_note_serial,
        before_swap_order, before_swap_update_css, before_wait_parts_closed,
        before_swap_order_S9, before_swap_order_M6)
    from step_algorithm import execute_step as _execute_step

    BINDINGS = (
        # TODO: reenable this eventually. Somehow.
        # ('_s', 'change_serial', 'Set Serial'),
        # ('ctrl+l', 'parse_for_info', 'Parse Info'),
        # TODO: This doesn't work
        Binding('ctrl+i', 'focus_input', 'Focus Input', show=False, priority=True),
    )
    # The step that gets switched to when switched to that phase (the first step of each phase)
    first_steps = {
        Phase.CONFIRM: Steps.pick_up_case,
        Phase.ROUTINE_CHECKS: Steps.ask_sunken_contacts,
        Phase.DEBUGGING: Steps.add_step,
        Phase.FINISH: Steps.ask_bit_mobility_done,
        Phase.SWAP: Steps.swap_unuse_parts,
        Phase.HOLD: Steps.hold_add_context,
        Phase.CHARGING: Steps.charging,
        Phase.UPDATING: Steps.updating,
    }

    phase_icons = {
        Phase.CONFIRM: "📋",
        Phase.ROUTINE_CHECKS: "📋",
        Phase.DEBUGGING: "🔧",
        Phase.SWAP: "🔃",
        Phase.FINISH: "✅",
        Phase.HOLD: "⏸️",
        Phase.CHARGING: "🪫",
        Phase.UPDATING: "💾",
    }

    phase = reactive(Phase.CONFIRM)
    step = reactive('')

    def __init__(self, id, color):
        # If the id has spaces, this will raise an error that gets caught by when we instantiate it
        super().__init__(id=f'case-{id}')
        self.ref = id
        # The serial numbers: first is the original, last is the current swap (or the original), and
        # anythinng in the middle is a DOA swap
        self.serials = []
        self._dock = ''
        # Set in set_color()
        self.color = color
        self._customer_states = ''
        self.repeat = False
        self._case_picked_up = False

        # The way this works, is it gets applied as "s" to the step when putting the current step into
        # the Input box. That way, any step that needs formatting can use it without messing up the
        # current step (as used by the step algorithm as states). It also gets reset to '' after
        # being used in the step setter (so set this before setting self.step)
        self.step_formatter = ''

        self.prev_step = None

        self._liquid_swap = None
        self._sunken_side = None

        self.text_area = CustomTextArea(self.ref)

        # We set this here, instead of when instantiating it, so it triggers the setter
        self.step = self.first_steps[Phase.CONFIRM]
        self.input = Input(placeholder=self.step, id='input_' + self.ref)
        self.input.cursor_blink = False
        self.sidebar = Sidebar(self)

        self.mobility_menu = MobilityMenu(self)
        self.external_notes_menu = ExternalNotesMenu(self)
        self.hints_menu = HintsMenu(self)
        self.cmd_menu = CommandsMenu()
        self.acronym_menu = AcronymMenu()

        # Some internal values to make auto guessing external notes easier
        self._bin_screw_has_rust = False
        self._dock_tank_screw_has_rust = False
        self._liquid_found = False
        # self._modular = True

        self._finish_first_copy_notes = ''
        self._also_check_left = False
        self._swap_after_battery_test = False
        self._swap_due_to_sunken_contacts = False
        # In the absense of info, assume it is
        self._is_current_swap_refurb = True

        self._step_after_manual_serial = None

        # This gets run on mount of the color selector
        # self.set_color(color)

        # TODO: this shouldn't be here, but pick_up_case as a first step isn't triggering side effects properly
        self.before_pick_up_case()

    # def on_mount(self):
        # We set this here, instead of when instantiating it, so it triggers the setter
        # self.step = self.first_steps[Phase.CONFIRM]

    def open_menu(self, event: Select.Changed):
        match event.value:
            case "Remove Double Lines":
                self.text_area.text = self.text_area.text.replace('\n\n', '\n')
            case 'Hints': self.hints_menu.action_toggle()
            case 'Commands': self.cmd_menu.action_toggle()
            case 'Acronyms': self.acronym_menu.action_toggle()
            case 'Update Sidebar': self.sidebar.update()

    @on(Select.Changed, "#color-selector")
    def set_color(self, event: Select.Changed):
        to_color = event.value
        self.color = to_color
        self.sidebar.styles.background = to_color
        self._tab.styles.background = to_color
        # Easier to just set it here rather than try to figure out how to reference them all via stylesheet
        self._tab.styles.color = 'black'

    def compose(self):
        yield self.text_area
        # with HorizontalGroup():
        yield self.mobility_menu
        yield self.external_notes_menu
        yield self.hints_menu
        yield self.cmd_menu
        yield self.acronym_menu
        yield self.input
        yield self.sidebar

        # We're doing this here, because it needs to be mounted before we can change the tab label
        self._tab.label = self.tab_label
        # self.sidebar.update()

        self.input.focus()

    def watch_step(self, old, new):
        # Because as a reactive attribute, it apparently runs before mounting (before compose is called)
        try:
            self.prev_step = old

            # self.text_area.text += '\n' + old + ' -> ' + new

            # If we have a method named `before_<step_name>`, then call it
            method_name = 'after_' + invert_dict(Steps.__dict__)[old]
            if hasattr(self, method_name):
                getattr(self, method_name)()

            # If we have a method named `after_<step_name>`, then call it
            method_name = 'before_' + invert_dict(Steps.__dict__)[new]
            if hasattr(self, method_name):
                getattr(self, method_name)()

            try:
                self.input.placeholder = new.format(s=self.step_formatter)
            except KeyError:
                self.input.placeholder = new

            self.step_formatter = ''

            self.save()
        except:
            pass

    def watch_phase(self, old, new):
        new_phase = Phase(new)
        if not self._case_picked_up:
            return

        # When switching to DEBUGGING phase from anywhere, ensure that Process: exists
        if new_phase == Phase.DEBUGGING:
            self.ensure_process()
            # I tried this and determined I didn't like it
            # TODO: add this as a setting
            # self.mobility_menu.visible = True
        self.sidebar.phase_selector.value = new_phase.value
        self._update_label()

        if self.phase == Phase.CONFIRM:
            self.step = self.first_steps[Phase.CONFIRM]# if not self.serial else Steps.check_repeat
        if self.phase == Phase.CHARGING:
            self.step = self.first_steps[self.phase]
        elif self.phase == Phase.SWAP:
            # If the first+ swap is DOA
            if len(self.serials) >= 2:
                # This is copied from next_step == 'order swap'
                if self.serial.startswith('s9'):
                    self.ensure_serial(Steps.swap_order_S9)
                elif self.serial.startswith('m6'):
                    self.ensure_serial(Steps.swap_order_M6)
                else:
                    self.ensure_serial(Steps.swap_order)
            else:
                self.ensure_serial(self.first_steps[self.phase])
        else:
            self.ensure_serial(self.first_steps[self.phase])

    @on(Select.Changed, "#phase-select")
    def on_phase_changed(self, event: Select.Changed) -> None:
        if self._case_picked_up:
            self.phase = Phase(event.value)
        else:
            self.sidebar.phase_selector.value = Phase.CONFIRM.value
        self.input.focus()

    def add_step(self, step, bullet='*'):
        # For consistency
        self.text_area.text = self.text_area.text.strip() + '\n'
        self.text_area.text += f'{bullet} {step.strip()}\n'

    def action_open_mobility_menu(self):
        # Only allow the mobility menu to be opened if we have information about the bot
        if self.serial and self.phase == Phase.DEBUGGING:
            self.mobility_menu.action_toggle()

    def action_open_external_notes_menu(self):
        # Only allow the mobility menu to be opened if we have information about the bot
        if self.serial:
            self.external_notes_menu.action_toggle()

    def action_change_serial(self):
        self.ensure_serial(self.step, force=True)

    def ensure_serial(self, next_step, *, force=False):
        """ If we don't have a serial number, ask for one manually, then go back to what we were
            doing. If we do have a serial number, just continue"""
        if not self.serial or force:
            self.step = Steps.manual_get_serial
            self._step_after_manual_serial = next_step
        else:
            self.step = next_step

    def serialize(self):
        return {
            'notes': self.text_area.text,
            'color': self.color,
            'ref': self.ref,
            'serials': self.serials,
            'phase': self.phase.value,
            'step': self.step,
            'todo': self.sidebar.todo.text,
            '_step_after_manual_serial': self._step_after_manual_serial,
        }

    @staticmethod
    def deserialize(data):
        case = Case(data['ref'], data.get('color', random.choice(list(COLORS.keys()))))
        case.text_area.text = data.get('notes', data['ref'] + '\n')
        try:
            case.serials = data['serials']
        except KeyError:
            case.serials = [data.get('serial', '') or '']
            if not case.serials[0]:
                case.serials = []
        # case.sidebar.update()
        case.sidebar.todo.text = data.get('todo', '')
        case.phase = Phase(data.get('phase', Phase.DEBUGGING))
        case.step = data.get('step', Steps.add_step)
        case._step_after_manual_serial = data.get('_step_after_manual_serial', None)
        case.sidebar.phase_selector.value = case.phase.value

        if case.step != Steps.pick_up_case:
            case._case_picked_up = True

        return case

    @staticmethod
    def attempt_load_case(ref:str) -> Union['Case', str]:
        if ref in EXISTING_CASES:
            # Make a backup before we overwrite it. To be safe.
            backup_path = EXISTING_CASES[ref].with_suffix('.bak')
            backup_path.write_bytes(EXISTING_CASES[ref].read_bytes())
            with EXISTING_CASES[ref].open('r') as f:
                return Case.deserialize(json.load(f))
        else:
            return ref

    def ensure_process(self):
        if 'Process:' not in self.text_area.text:
            self.text_area.text = self.text_area.text.strip() + '\n\nProcess:\n'

    def ensure_context(self):
        if 'CONTEXT:' not in self.text_area.text:
            self.text_area.text = self.text_area.text.strip() + '\n\nCONTEXT:\n'

    def on_input_submitted(self, event):
        if event.input.id == f'input_{self.ref}':
            self._execute_step(event.value)
            self.input.value = ''

    def action_focus_input(self):
        self.input.focus()

    def save(self):
        with open(SAVE_NOTES_PATH / (self.ref + '.txt'), 'w') as f:
            f.write(self.text_area.text)

        with open(SAVE_CASE_PATH / (self.ref + '.json'), 'w') as f:
            json.dump(self.serialize(), f)

    @staticmethod
    def snap_to_dock(name):
        """ Make the dock one of the allowed docks
            this parses input given from the ask for dock step, parses it, and returns the dock
        """
        if name:
            input = capitolize(name.split(',')[0].strip())
            return get_close_matches(input, DOCKS + ('Alex-Albany',), n=1, cutoff=0.0)[0]
        else:
            return ""

    def add_measure_contacts_step(self, side, measurements):
        meas = mean(measurements)
        # meas = round(meas, 1 if 3.8 > meas > 3.74 else 2)
        meas = round(meas, 1)
        self.add_step(f'Measured {"right" if side == "r" else "left"} contact: {meas}mm +/- {std(measurements):.2f} ({len(measurements)} measurements)')

    # Helper methods
    def get_quick_model(self):
        if not self.serials:
            return ''
        elif self.serial[0] == 'r':
            return self.serial[1:4]
        else:
            return self.serial[:2].upper()

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

    def require_battery_test(self):
        cx_states = self.customer_states.lower()
        return (
            'charg' in cx_states
            or
            'batt' in cx_states
            or
            # "doesn't turn on" or "does not turn on"
            't turn on' in cx_states
            or
            self._liquid_found
        )

    def log(self, action):
        with LOG_PATH.open('a') as f:
            f.write('{action},{id},{color},{serial},{timestamp}\n'.format(
                action=action,
                id=self.ref,
                color=COLORS[self.color],
                # Yes, the current one. This is intentional.
                serial=self.serial,
                timestamp=datetime.now(),
            ))

    def _update_label(self):
        if self._tab:
            self._tab.label = self.tab_label

    @property
    def _tab(self):
        try:
            return self.parent.parent.parent.get_tab(self.parent.id)
        except AttributeError:
            return

    @property
    def tab_label(self):
        s = ''
        if self.repeat:
            s += 'R '
        s += self.ref

        if settings.INCLUDE_MODEL_IN_TAB:
            model = self.get_quick_model()
            if model:
                s += ' • ' + model

        s += f' [on {darken_color(self.color, .6)}]'
        # To distinguish cases that are on my bench charging, from once that aren't
        if self.phase == Phase.CHARGING:
            if "Routine Check" in self.text_area.text:
                s += "🔋"
            else:
                s += "🪫"
        else:
            s += self.phase_icons[self.phase]
        return s

    @property
    def can_mop(self):
        return self.serial.startswith(('m', 'c'))

    @property
    def can_vacuum(self) -> bool:
        return not self.serial.startswith('m')

    @property
    def is_dock(self) -> bool:
        return bool(self.dock) and self.dock.lower() not in ('bombay', 'san marino', 'torino')

    @property
    def dock_can_refill(self):
        return bool(self.dock) and self.dock.lower() in ('aurora', 'boulder')

    @property
    def is_combo(self):
        if self.serial:
            return self.serial.lower().startswith('c')
        else:
            return None

    @property
    def is_factory_lapis(self):
        """ True if *any* of the serials are a factory lapis, not just the current one """
        if self.serial.startswith(('e', 'r')):
            return False
        try:
            return any(i[3] == '7' for i in self.serials)
        except IndexError:
            return False

    @property
    def has_lapis(self):
        return 'lapis' in self.text_area.text.lower()

    @property
    def notes(self):
        return self.text_area.text

    @notes.setter
    def set_notes(self, to):
        self.text_area.text = to

    @property
    def serial(self):
        if self.serials:
            # It would be great if this were actually upper(), switching it would be a major refactor
            return self.serials[-1].lower()
        else:
            return None

    def add_serial(self, serial):
        # It would be great if this were actually upper(), switching it would be a major refactor
        self.serials.append(serial.lower())
        # The sidebar always uses the last serial to load info
        self.sidebar.update()

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
    def is_swap(self):
        return len(self.serials) > 1

    @property
    def has_weird_i5g(self):
        return any(i.startswith('i5g') for i in self.serials)

    @property
    def bin_screw_has_rust(self):
        if self._bin_screw_has_rust is None :
            self._bin_screw_has_rust = bool(re.search(
                r'Routine\ Checks(?:(?:.|\n))+\*\ (?:Tank\ float\ screw\ has\ a\ spot\ of\ rust\ on\ it|Tank\ float\ screw\ is\ entirely\ rusted)(?:(?:.|\n))+Process:',
                self.text_area.text
            ))
        return self._bin_screw_has_rust

    @property
    def dock_tank_screw_has_rust(self):
        if self._dock_tank_screw_has_rust is None:
            self._dock_tank_screw_has_rust = bool(re.search(
                r'Routine\ Checks(?:(?:.|\n))+\*\ (?:Dock tank\ float\ screw\ has\ a\ spot\ of\ rust\ on\ it|Dock tank\ float\ screw\ is\ entirely\ rusted)(?:(?:.|\n))+Process:',
                self.text_area.text
            ))
        return self._dock_tank_screw_has_rust

    @property
    def liquid_found(self):
        if self._liquid_found is None:
            self._liquid_found = bool(re.search(
                r'Routine\ Checks(?:(?:.|\n))+\*\ Found\ signs\ of\ liquid\ (?:(?:.|\n))+Process:',
                self.text_area.text
            ))
        return self._liquid_found

    @property
    def customer_states(self):
        if not self._customer_states:
            # "Customer States: " + group(+anything)
            if (found := re.search(r'Customer\ States:\ ((?:.)+)', self.text_area.text)):
                self._customer_states = found.group(1)
        return self._customer_states

    @property
    def dock(self):
        if not self._dock:
            # "Parts in: " + either(+either(digit, letter), "Robot") + optional(', ' + group(word))
            if (found := re.search(r'Parts\ in:\ (?:(?:(?:\d|[A-Za-z]))+|Robot)(?:,\ (\w+))?', self.text_area.text)):
                self._dock = found.group(1)
        return self._dock or ''
