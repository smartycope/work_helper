from textual.containers import *
from textual.reactive import reactive
from textual.widgets import *
from Phase import Phase
from texts import Steps
from CustomTextArea import CustomTextArea
from Sidebar import Sidebar
from MobilityMenu import MobilityMenu


class Case(VerticalGroup):
    from step_algorithm import execute_step as _execute_step

    BINDINGS = (
        ('ctrl+m', 'open_mobility_menu', 'Mobility'),
    )

    step = reactive(Steps.confirm_id)
    phase = reactive(Phase.CONFIRM)

    # The step that gets switched to when switched to that phase (the first step of each phase)
    first_steps = {
        Phase.ROUTINE_CHECKS: Steps.ask_sunken_contacts,
        Phase.DEBUGGING: Steps.add_step,
        Phase.FINISH: Steps.ask_final_cleaned,
        Phase.SWAP: Steps.swap_email,
    }

    def __init__(self, id, color):
        # If the id has spaces, this will raise an error that gets caught by when we instantiate it
        super().__init__(id=f'case-{id}')
        self.ref = id
        self.serial = None
        self.dock = None
        # Set in set_color()
        self.color = color
        self.customer_states = None

        self.prev_step = None

        self._liquid_swap = None
        self._sunken_side = None

        self.text_area = CustomTextArea(self.ref)

        self.input = Input(placeholder=self.step, id='input_' + self.ref)
        self.input.cursor_blink = False
        self.sidebar = Sidebar(self)

        self.mobility_menu = MobilityMenu(self)

        # This gets run on mount of the color selector
        # self.set_color(color)

    def set_color(self, to_color):
        # old_color = self.color
        self.color = to_color
        self.sidebar.styles.background = to_color
        self.parent.parent.parent.get_tab(self.parent.id).styles.background = to_color
        # Easier to just set it here rather than try to figure out how to reference them all via stylesheet
        self.parent.parent.parent.get_tab(self.parent.id).styles.color = 'black'

    def compose(self):
        yield self.text_area
        yield self.mobility_menu
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
        # For consistency
        self.text_area.text = self.text_area.text.strip() + '\n'
        self.text_area.text += f'{bullet} {step}\n'

    def on_select_changed(self, event: Select.Changed) -> None:
        match event.select.id:
            case "color-selector":
                self.set_color(event.value)
            case "phase-select":
                self.phase = Phase(event.value)
                match self.phase:
                    case Phase.CONFIRM:
                        # At first, we want to confirm ids, not just get the model number
                        self.step = Steps.ask_labels if not self.serial else Steps.check_repeat
                    case _:
                        self.ensure_serial(self.first_steps[self.phase])

    def action_open_mobility_menu(self):
        # Only allow the mobility menu to be opened if we have information about the bot
        self.mobility_menu.visible = bool(self.serial)

    def ensure_serial(self, next_step):
        """ If we don't have a serial number, ask for one manually, then go back to what we were
            doing. If we do have a serial number, just continue"""
        if not self.serial:
            self.step = Steps.manual_get_serial
            self._step_after_manual_serial = next_step
        else:
            self.step = next_step

    def serialize(self):
        return {
            'notes': self.text_area.text,
            'color': self.color,
            'ref': self.ref,
            'serial': self.serial,
            'todo': self.sidebar.todo.text
        }

    @staticmethod
    def deserialize(data):
        case = Case(data.get('ref', ''), data.get('color', ''))
        case.text_area.text = data.get('notes', '')
        case.serial = data.get('serial', '')
        case.sidebar.todo.text = data.get('todo', '')
        return case

    def on_input_submitted(self, event):
        if event.input.id == f'input_{self.ref}':
            self._execute_step(event.value)
            self.input.value = ''

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

    @property
    def is_mopper(self):
        return self.serial.startswith(('m', 'c'))

    @property
    def is_dock(self):
        return self.dock.lower() not in ('Bombay', 'San Marino', 'Torino')

    @property
    def is_combo(self):
        if self.serial:
            return self.serial.lower().startswith('c')
        else:
            return None
