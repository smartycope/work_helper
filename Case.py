import json
import re
from HintsMenu import HintsMenu
# from MenuMenu import MenuMenu
from globals import COLORS, LOG_PATH, SAVE_CASE_PATH, SAVE_NOTES_PATH, darken_color, invert_dict
import random
from textual.containers import *
from textual.reactive import reactive
from textual.widgets import *
from Phase import Phase
from texts import Steps
from CustomTextArea import CustomTextArea
from Sidebar import Sidebar
from MobilityMenu import MobilityMenu
from CommandsMenu import CommandsMenu
from ExternalNotesMenu import ExternalNotesMenu
from textual import on
from datetime import datetime


class Case(VerticalGroup):
    from step_algorithm import execute_step as _execute_step
    from step_algorithm import (
        before_pick_up_case,
        after_pick_up_case,
        after_ask_complete_case_CSS,
        before_generate_external_notes,
        after_generate_external_notes,
        # before_ask_copy_notes_1,
        before_ask_double_check,
        before_ask_copy_notes_2,
        before_ask_complete_case_CSS,
        before_swap_update_css,
        before_swap_email,
        before_swap_order,
        before_swap_note_serial,
        before_hold_copy_notes_to_CSS,
        before_wait_parts_closed,
        before_hold_add_context,
    )
    from parse_commands import parse_command

    BINDINGS = (
        # TODO: reenable this eventually. Somehow.
        # ('_s', 'change_serial', 'Set Serial'),
        # ('ctrl+l', 'parse_for_info', 'Parse Info'),
        # TODO: This doesn't work
        Binding('ctrl+i', 'focus_input', 'Focus Input', show=False, priority=True),
    )
    # The step that gets switched to when switched to that phase (the first step of each phase)
    first_steps = {
        Phase.CONFIRM: Steps.confirm_id,
        Phase.ROUTINE_CHECKS: Steps.ask_sunken_contacts,
        Phase.DEBUGGING: Steps.add_step,
        Phase.FINISH: Steps.ask_bit_mobility_done,
        Phase.SWAP: Steps.swap_unuse_parts,
        Phase.HOLD: Steps.hold_add_context,
    }

    phase_icons = {
        Phase.CONFIRM: "📋",
        Phase.ROUTINE_CHECKS: "📋",
        Phase.DEBUGGING: "🔧",
        Phase.SWAP: "🔃",
        Phase.FINISH: "✅",
        Phase.HOLD: "⏸️",
    }

    phase = reactive(Phase.CONFIRM)
    step = reactive(first_steps[Phase.CONFIRM])

    def __init__(self, id, color):
        # If the id has spaces, this will raise an error that gets caught by when we instantiate it
        super().__init__(id=f'case-{id}')
        self.ref = id
        # The serial numbers: first is the original, last is the current swap (or the original), and
        # anythinng in the middle is a DOA swap
        self.serials = []
        self.dock = None
        # Set in set_color()
        self.color = color
        self.customer_states = ''

        # The way this works, is it gets applied as "s" to the step when putting the current step into
        # the Input box. That way, any step that needs formatting can use it without messing up the
        # current step (as used by the step algorithm as states). It also gets reset to '' after
        # being used in the step setter (so set this before setting self.step)
        self.step_formatter = ''

        self.prev_step = None

        self._liquid_swap = None
        self._sunken_side = None

        self.text_area = CustomTextArea(self.ref)

        self.input = Input(placeholder=self.step, id='input_' + self.ref)
        self.input.cursor_blink = False
        self.sidebar = Sidebar(self)

        self.mobility_menu = MobilityMenu(self)
        self.external_notes_menu = ExternalNotesMenu(self)
        self.hints_menu = HintsMenu(self)
        self.cmd_menu = CommandsMenu()

        # Some internal values to make auto guessing external notes easier
        self._bin_screw_has_rust = False
        self._dock_tank_screw_has_rust = False
        self._liquid_found = False
        # self._modular = True

        self._finish_first_copy_notes = ''
        self._also_check_left = False
        self._swap_after_battery_test = False
        self._swap_due_to_sunken_contacts = False

        # This gets run on mount of the color selector
        # self.set_color(color)

    def open_menu(self, event: Select.Changed):
        match event.value:
            case "Remove Double Lines":
                self.text_area.text = self.text_area.text.replace('\n\n', '\n')
            case 'Hints': self.hints_menu.action_toggle()
            case 'Commands': self.cmd_menu.action_toggle()
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
        yield self.input
        yield self.sidebar

        # We're doing this here, because it needs to be mounted before we can change the tab label
        self._tab.label = self.tab_label

        self.input.focus()

    def watch_step(self, old, new):
        # Because as a reactive attribute, it apparently runs before mounting (before compose is called)
        try:
            self.save()

            self.prev_step = old

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
        except:
            pass

    def watch_phase(self, old, new):
        new_phase = Phase(new)
        # When switching to DEBUGGING phase from anywhere, ensure that Process: exists
        if new_phase == Phase.DEBUGGING:
            self.ensure_process()
            # I tried this and determined I didn't like it
            # TODO: add this as a setting
            # self.mobility_menu.visible = True
        self.sidebar.phase_selector.value = new_phase.value
        if self._tab:
            self._tab.label = self.tab_label
        # self.query_one(f'#tab-pane-{self.ref}').title = self.ref + ' ' + self.phase_icons[new_phase]


    def add_step(self, step, bullet='*'):
        # For consistency
        self.text_area.text = self.text_area.text.strip() + '\n'
        self.text_area.text += f'{bullet} {step.strip()}\n'

    @on(Select.Changed, "#phase-select")
    def on_phase_changed(self, event: Select.Changed) -> None:
        self.phase = Phase(event.value)

        if self.phase == Phase.CONFIRM:
            self.step = self.first_steps[Phase.CONFIRM] if not self.serial else Steps.check_repeat
        else:
            self.ensure_serial(self.first_steps[self.phase])

        self.input.focus()

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
        case.sidebar.update()
        case.sidebar.todo.text = data.get('todo', '')
        case.phase = Phase(data.get('phase', Phase.DEBUGGING))
        case.step = data.get('step', Steps.add_step)
        case.sidebar.phase_selector.value = case.phase.value
        case.action_parse_for_info()
        return case

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

    def action_parse_for_info(self):
        """ Parse the currently set text for things like the dock, customer states, things like that """
        # "Parts in: Robot" + group(optional(', ' + word))
        if (found := re.search(r'Parts\ in:\ Robot((?:,\ \w+)?)', self.text_area.text)):
            self.dock = found.group(1)

        # "Customer States: " + group(+anything)
        if (found := re.search(r'Customer\ States:\ ((?:.)+)', self.text_area.text)):
            self.customer_states = found.group(1)

        # 'Routine Checks' + match_max(literallyAnything) + '* ' + chunk + ... + match_max(literallyAnything) + 'Process:'
        # self._modular = not bool(re.search(r'Routine\ Checks(?:(?:.|\n))+\*\ .+is\ non\-modular(?:(?:.|\n))+Process:', self.text_area.text))
        self._bin_screw_has_rust = bool(re.search(r'Routine\ Checks(?:(?:.|\n))+\*\ (?:Tank\ float\ screw\ has\ a\ spot\ of\ rust\ on\ it|Tank\ float\ screw\ is\ entirely\ rusted)(?:(?:.|\n))+Process:', self.text_area.text))
        self._dock_tank_screw_has_rust = bool(re.search(r'Routine\ Checks(?:(?:.|\n))+\*\ (?:Dock tank\ float\ screw\ has\ a\ spot\ of\ rust\ on\ it|Dock tank\ float\ screw\ is\ entirely\ rusted)(?:(?:.|\n))+Process:', self.text_area.text))
        self._liquid_found = bool(re.search(r'Routine\ Checks(?:(?:.|\n))+\*\ Found\ signs\ of\ liquid\ (?:(?:.|\n))+Process:', self.text_area.text))

    def action_focus_input(self):
        self.input.focus()

    def save(self):
        with open(SAVE_NOTES_PATH / (self.ref + '.txt'), 'w') as f:
            f.write(self.text_area.text)

        with open(SAVE_CASE_PATH / (self.ref + '.json'), 'w') as f:
            json.dump(self.serialize(), f)

    # TODO
    def snap_to_dock(self, name):
        """ Make the dock one of the allowed docks """
        return name

    # Helper methods
    def get_quick_model(self):
        if self.serial[0] == 'r':
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
            return 'DCT won\'t work, only BBK'
        elif self.serial.startswith(('i3', 'i4', 'i5')):
            return 'Any of the bumper tests can fail'
        elif self.serial.startswith('j9'):
            return 'If v2 (clip battery), can fail basically everything. Otherwise, second dock comms test, if FW == 24.29.x (ensure robot still evacs)'
        elif self.serial.startswith('j'):
            return 'Second dock comms test, if FW == 24.29.x (ensure robot still evacs)'
        elif self.serial.startswith('s9'):
            return 'Low-current vacuum test, pass if the value is <1500'
        elif self.serial.startswith('m'):
            return 'Pad detection test (run both wet and dry missions). If the sprayer on current is too low, charge and try again'
        elif self.serial.startswith('c'):
            text = 'Actuator arm current and speed tests, if FW >= 23.53.6 (ensure it deploys in mobility mission). If FW >= v24.29.5, DCT is brand new. FW >= v24.29.1: dock comms can fail'
            if self.serial.startswith('c9'):
                text = 'Sprayer current off, but note the firmware version. ' + text
            return text
        else:
            return 'Optical bin tests (at most 2, if barely out of range)'

    def get_notes(self):
        # if self.serial.startswith('j'):
            # return 'If the last digit of the SPL SKU is 7, they have a Lapis bin at home! If the middle number is 1, it came with just a home base. In that case, don\'t test on a dock! Just a base.'
        notes = ''
        if self.serial.startswith('c9'):
            notes += "[on orange_red1]Remember to remove battery before removing the CHM[/]. Also, if the DCT card doesn't work, try a hard reset\nc955 -> albany; c975 -> aurora"

        if self.serial.startswith('i'):
            notes += 'If having weird trouble with DCT, try factory reset'

        if self.serial.startswith(('r', 'e')):
            notes += 'To BiT: lights have to be off (hold down clean to turn off), then hold home & clean and press spot 5x. Then press home to start the tests. Spot is prev, home is next. Hold clean when finished successfully, otherwise factory reset.'

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
        elif self.serial.startswith(('c10', 'x')):
            return ['Boulder', 'Aurora'] + camera
        elif self.serial.startswith('c9'):
            return ['Aurora'] + camera
        elif self.serial.startswith(('j', 'c')):
            return camera
        else:
            return ir

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

    @property
    def _tab(self):
        try:
            return self.parent.parent.parent.get_tab(self.parent.id)
        except AttributeError:
            return

    @property
    def tab_label(self):
        return self.ref + f' [on {darken_color(self.color, .6)}]' + self.phase_icons[self.phase]

    @property
    def can_mop(self):
        return self.serial.startswith(('m', 'c'))

    @property
    def can_vacuum(self) -> bool:
        return not self.serial.startswith('m')

    @property
    def is_dock(self) -> bool:
        return self.dock.lower() not in ('bombay', 'san marino', 'torino') and bool(self.dock)

    @property
    def dock_can_refill(self):
        return self.dock.lower() in ('aurora', 'boulder')

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

    # @on(CustomTextArea.OpenMobilityMenu)
    # def deleteme(self):
        # self.text_area.text += 'IT WORKED'
