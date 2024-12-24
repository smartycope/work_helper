from enum import Enum
from pathlib import Path
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.containers import *# HorizontalGroup, VerticalScroll
from textual.document._document import Selection
from textual.widgets import *#Footer, Header, TextArea
from collections import OrderedDict
from clipboard import copy
import textwrap

SIDEBAR_WIDTH = 30
DEBUG = True


# TODO: make the copy button not focusable

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
    confirm_id = 'Confirm IDs'
    check_repeat = 'Check if case is a repeat'
    check_spl_sku = 'Check that the SPL SKU is valid'
    pick_up_case = 'Go pick up the case on CSS (case ID copied)'
    ask_dock = 'Additional dock'
    ask_damage = 'Additional damage'
    customer_states = 'Customer States'
    check_liquid_damage = 'Signs of liquid damage (empty for no)'
    ask_sunken_contacts = 'Sunken contacts (empty for no)'
    ask_blower_play = 'Play in blower motor (empty for no)'
    ask_rollers = 'Extractors are good (empty for yes)'
    ask_s9_lid_pins = 'Are the lid pins sunken (empty for no)'
    ask_cleaned = 'Robot cleaned ("na" if not, notes or empty if so)'
    battery_test = 'Battery test (current, health): '
    ask_user_base_contacts = 'Are the charging contacts on the user base good (empty for yes)'
    ask_charge_customer_dock = "What's the charging wattage on the customer's dock"
    ask_charge_test_dock = "What's the charging wattage on a test base"

    liquid_check_corrosion = 'Is there corrosion on the board or connections (specify or empty for no)'
    liquid_check_dock = 'Is there liquid residue in the user dock (empty for no)'
    liquid_check_dock_bin = 'Is there liquid residue in the robot bin (empty for no)'
    liquid_take_pictures = 'Take pictures of liquid residue'

    sunken_ask_side = 'Which side is sunken (R/L)'
    sunken_ask_measurement = 'Contact measurement'

    add_step = 'Add Step'

class CustomTextArea(TextArea):
    BINDINGS = [b for b in TextArea.BINDINGS if b.key != "home,ctrl+a"] + [
        Binding('ctrl+a', 'select_all', 'Select All', show=False),
        Binding('alt+j', 'cursor_left', 'Cursor Left', show=False),
        Binding('alt+l', 'cursor_down', 'Cursor Down', show=False),
        Binding('alt+;', 'cursor_right', 'Cursor Right', show=False),
        Binding('alt+k', 'cursor_up', 'Cursor Up', show=False),
        Binding('esc,ctrl+b', 'unfocus', 'Unfocus', show=False),
        Binding("home","cursor_line_start","Cursor line start",show=False),
    ]

    def __init__(self, ref):
        super().__init__(ref + '\n', id='textarea_' + ref)
        self.cursor_blink = False

    # TODO: This doesn't work
    def unfocus(self):
        self.parent.focus()

    # def watch_text(self, *args):
    #     super().watch_text(*args)
    #     self.scroll_to(None, 1000, animate=False)

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
            notes = textwrap.fill(self.case.get_notes(), SIDEBAR_WIDTH)
            if notes:
                self.notes_sep.update(f'{" Notes ":-^{SIDEBAR_WIDTH}}')
                self.notes.update(notes)

    def compose(self):
        yield Label(f'{self.case.ref:^{SIDEBAR_WIDTH}}\n')
        yield Label(f'{" Model ":-^{SIDEBAR_WIDTH}}')
        self.model = Label('')
        yield self.model
        yield Label(f'{" Sleep Mode ":-^{SIDEBAR_WIDTH}}')
        self.sleep_mode = Label('')
        yield self.sleep_mode
        yield Label(f'{" Factory Reset ":-^{SIDEBAR_WIDTH}}')
        self.factory_reset = Label('')
        yield self.factory_reset
        yield Label(f'{" DCT ":-^{SIDEBAR_WIDTH}}')
        self.dct = Label('')
        yield self.dct
        self.notes_sep = Label('')
        yield self.notes_sep
        self.notes = Label('')
        yield self.notes
        button = Button('Copy Notes', id='copy-button')
        button.can_focus = False
        yield button

        yield Label('TODO context:')
        ta = TextArea(id='lower-sidebar')
        ta.can_focus = False
        yield ta

    def on_button_pressed(self, event: Button.Pressed):
        copy(self.case.text_area.text)

class Case(VerticalGroup):
    # BINDINGS = [("n", "new_case", "New Case")]
    step = reactive(Steps.confirm_id)

    def __init__(self, id, color):
        # super().__init__(id='case_'+id.replace(' ', '_'))
        super().__init__(id='case_'+str(color))
        self.ref = id
        self.serial = None
        self.dock = None
        self.color: int = color
        self.customer_states = None
        self.phase = Phase.CONFIRM

        self.prev_step = None

        self._liquid_swap = None
        self._sunken_side = None

    def compose(self):
        self.text_area = CustomTextArea(self.ref)
        self.input = Input(placeholder=self.step, id='input_' + self.ref)
        self.input.cursor_blink = False
        self.sidebar = Sidebar(self)
        # with VerticalGroup() as vg:
        #     yield Static('Test')

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

    def add_step(self, step):
        self.text_area.text += f'* {step}\n'

    # The main algorithm is here
    def on_input_submitted(self):
        resp = self.input.value
        self.input.value = ''

        # TODO: I think back isn't working
        if resp.lower() == 'back' and self.step != Steps.confirm_id:
            self.step = self.prev_step
            return

        match self.step:
            # Main path
            case Steps.confirm_id:
                ids=  resp.lower()
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
                    self.text_area.text += ', ' + resp
                self.text_area.text += '\n'
                self.step = Steps.customer_states

            case Steps.customer_states:
                if resp:
                    self.customer_states = resp
                    self.text_area.text += 'Customer States: ' + resp + '\n\nRoutine Checks:\n'
                    self.step = Steps.check_liquid_damage

            case Steps.check_liquid_damage:
                if resp.lower() == 'na':
                    self.step = Steps.ask_sunken_contacts
                elif resp:
                    self.add_step('Found signs of liquid residue')
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
                        self.add_step('Found play in blower motor')
                    else:
                        self.add_step('No play in blower motor')
                self.step = Steps.ask_rollers

            case Steps.ask_rollers:
                if resp and resp.lower() != 'na':
                    self.add_step('Rollers are bad')

                if self.serial.lower().startswith('s'):
                    self.step = Steps.ask_s9_lid_pins
                else:
                    self.step = Steps.ask_cleaned

            # TODO: extend this in the future to go into swap
            case Steps.ask_s9_lid_pins:
                if resp:
                    self.add_step('Lid pins are sunken')
                self.step = Steps.ask_cleaned

            case Steps.ask_cleaned:
                if resp.lower() != 'na':
                    self.add_step('Cleaned robot' + ((' - ' + resp) if resp else ''))

                self.step = Steps.ask_user_base_contacts

            case Steps.ask_user_base_contacts:
                if resp.lower() != 'na':
                    self.add_step(f"Charging contacts on the customer's {self.dock} look {'good' if not resp else 'bad'}")

                if 'charg' in self.customer_states.lower() and self.dock:
                    self.step = Steps.battery_test

                self.step = Steps.ask_charge_customer_dock if self.dock else Steps.ask_charge_test_dock

            case Steps.battery_test:
                if resp.lower() != 'na':
                    charge, health = resp.split(',')
                    self.add_step(f'Tested battery: {charge.strip()}%/{health.strip()}%')

                self.step = Steps.ask_charge_customer_dock if self.dock else Steps.ask_charge_test_dock

            case Steps.ask_charge_customer_dock | Steps.ask_charge_test_dock:
                if resp.lower() != 'na':
                    try:
                        watts = round(float(resp))
                    except ValueError:
                        self.add_step(resp)
                        return

                    dock = f'customer {self.dock}' if self.dock else 'test base'

                    if watts < 3:
                        self.add_step(f"Robot does not charge on {dock} @ ~{watts}W")
                    elif watts < 10:
                        self.add_step(f"Robot charges on {dock} @ ~{watts}W (battery is full)")
                    else:
                        self.add_step(f"Robot charges on {dock} @ ~{watts}W")

                self.step = Steps.add_step

            # Liquid damage path
            case Steps.liquid_check_corrosion:
                if resp.lower() != 'na':
                    if resp:
                        self.add_step(f'Found signs of liquid corrosion on the {resp}')
                        self._liquid_swap = True
                    else:
                        self.add_step('No signs of liquid damage on the main board or connections')

                if self.dock:
                    self.step = Steps.liquid_check_dock
                else:
                    self.step = Steps.liquid_check_dock_bin

            case Steps.liquid_check_dock:
                if resp.lower() != 'na':
                    if resp:
                        self.add_step(f'Liquid residue found in the user {self.dock}')
                    else:
                        self.add_step(f'No signs of liquid residue found in the user {self.dock}')
                self.step = Steps.liquid_check_dock_bin

            case Steps.liquid_check_dock_bin:
                if resp.lower() != 'na':
                    if resp:
                        self.add_step('Liquid residue found in customer bin: probably sucked up liquid')
                    else:
                        self.add_step('No liquid residue found in customer bin')
                self.step = Steps.liquid_take_pictures

            # TODO connect to finish phase
            case Steps.liquid_take_pictures:
                if self._liquid_swap:
                    self.add_step('Diagnosis: Liquid damage')
                    self.add_step('Swap robot')
                    self.phase = Phase.FINISH
                    self.step = Steps.add_step
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
                    self.add_step(f'Diagnosis: Sucken {self._sunken_side} contact')
                    self.add_step('Swap robot' + (f' and customer {self.dock}' if self.dock else ''))
                    self.phase = Phase.FINISH
                    self.step = Steps.add_step

                self.step = Steps.ask_blower_play

            # Add Step phase
            case Steps.add_step:
                if self.phase == Phase.ROUTINE_CHECKS:
                    self.phase = Phase.DEBUGGING
                    self.text_area.text += '\nProcess:\n'
                self.add_step(resp)

        self.text_area.scroll_to(None, 1000, animate=False)

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
        elif self.serial.startswith(('j8', 'q7', 'i6', 'i7', 'i8')):
            return 'Green card'
        elif self.serial.startswith('m6'):
            return 'Small debug card, use Trident driver'
        elif self.serial.startswith(('j9', 'c9')):
            return 'Blue card'
        elif self.serial.startswith('e'):
            return 'Green card with micro USB plugged into right side'
        elif self.serial.startswith(('j7', 'c7')):
            return 'Green or Blue card. Try the Green card first'
        else:
            return 'Error: Model from serial number not recognized'

    def get_notes(self):
        if self.serial.startswith('j'):
            return 'If the last digit of the SPL SKU is 7, they have a Lapis bin at home! If the middle number is 1, it came with just a home base. In that case, don\'t test on a dock! Just a base.'
        return ''


if DEBUG:
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


    with open('~/Documents/deleteme_log.txt', 'w') as f:
        f.write('')

    _print = print
    def print(*a, **kw):
        with open('~/Documents/deleteme_log.txt', 'a') as log:
            _print(*a, file=log, **kw)

class HelperApp(App):
    BINDINGS = [
        ("n", "new_case", "New Case"),
        ("c", "close_case", "Close Case"),
        Binding('ctrl+tab', 'next_tab', 'Next Tab', show=True, priority=True),
        Binding('ctrl+shift+tab', 'prev_tab', 'Previous Tab', show=True, priority=True),
    ]
    CSS = '''
        #reference_popup {
            layer: above;
            content-align: center middle;
            align: center middle;
            width: 100%;
            # position: absolute;
            # top: 50%;
            # left: 50%;
            # transform: translate(-50%, -50%);
        }
        TabbedContent #--content-tab-pane-0 {
            background: #377a11;
            color: black;
        }
        TabbedContent #--content-tab-pane-1 {
            background: #ef9e16;
            color: black;
        }
        TabbedContent #--content-tab-pane-2 {
            background: #d1dd0b;
            color: black;
        }
        TabbedContent #--content-tab-pane-3 {
            background: #ea9daf;
            color: black;
        }
        TabbedContent #--content-tab-pane-4 {
            background: #799fad;
            color: black;
        }

        #sidebar-0 {
            dock: right;
            height: 100%;
            width: [SIDEBAR_WIDTH];
            background: #377a11;
            color: black;
        }
        #sidebar-1 {
            dock: right;
            height: 100%;
            width: [SIDEBAR_WIDTH];
            background: #ef9e16;
            color: black;
        }
        #sidebar-2 {
            dock: right;
            height: 100%;
            width: [SIDEBAR_WIDTH];
            background: #d1dd0b;
            color: black;
        }
        #sidebar-3 {
            dock: right;
            height: 100%;
            width: [SIDEBAR_WIDTH];
            background: #ea9daf;
            color: black;
        }
        #sidebar-4 {
            dock: right;
            height: 100%;
            width: [SIDEBAR_WIDTH];
            background: #799fad;
            color: black;
        }

        #copy-button{
            height: 3;
            width: 100%;
            dock: bottom;
        }

    '''.replace('{', '{{').replace('}', '}}').replace('[', '{').replace(']', '}').format(SIDEBAR_WIDTH=SIDEBAR_WIDTH)

    def __init__(self):
        super().__init__()
        self.cases = []
        self.dir = Path.home() / 'Documents' / 'Case_Notes'
        self.dir.mkdir(parents=True, exist_ok=True)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        popup = Input(placeholder='Case ID', id='reference_popup')
        popup.visible = False

        # yield Header('Helper')
        # with TabbedContent(id='tabs'):
        yield TabbedContent(id='tabs')
        #     for cnt, tmp in enumerate({
        #     '12345IR': ex1,
        #     '11111IR': ex2,
        #     '54321IR': ex3,
        #     '54321IR': ex3,
        #     '54321IR': ex3,
        # }.items()):
        #         ref, case = tmp
        #         with TabPane(ref, id='pane-'+str(cnt)):
        #             yield case
        # So we can still have access to the tabs
        # self.tabs = self.query('#tabs')
        yield popup
        yield Footer()

    def on_input_submitted(self):
        popup = self.query_one('#reference_popup')
        tabs = self.query_one('#tabs')
        # This should be the only way cases get deployed
        if popup.visible:
            popup.visible = False
            ref = popup.value
            popup.value = ''
            if len(self.cases) < 5:
                unused_color = (set(range(5)) - {i.color for i in self.cases}).pop()
                case = Case(ref, unused_color)
                self.cases.append(case)
                tabs.add_pane(TabPane(ref, case, id='pane-'+str(unused_color)))

    def action_new_case(self):
        """Add a new tab."""
        print('new case popup!')
        popup = self.query_one('#reference_popup')
        popup.visible = True
        popup.focus()

    def action_close_case(self):
        self.save()
        self.cases.remove(self.active_case)
        tabs = self.query_one('#tabs')
        tabs.remove_pane(tabs.active_pane.id)

    @property
    def active_case(self):
        tabs = self.query_one(TabbedContent)
        return tabs.active_pane.children[0]

    def action_remove(self) -> None:
        """Remove active tab."""
        tabs = self.query_one(TabbedContent)
        active_tab = tabs.active_tab
        if active_tab is not None:
            self.save()
            self.cases.remove(self.active_case)
            tabs.remove_tab(active_tab.id)

    def next_tab(self):
        print('next tab called')
        tabs = self.query_one(TabbedContent)
        print(f'active case:', self.active_case.ref)
        idx = self.cases.index(self.active_case)
        next = self.cases[(idx+1)%len(self.cases)]
        print(f'next case:', next.ref)
        tabs.active = f'pane-{next.color}'

    def prev_tab(self):
        print('prev tab called')
        tabs = self.query_one(TabbedContent)
        idx = self.cases.index(self.active_case)
        prev = self.cases[idx-1]
        tabs.active = f'pane-{prev.color}'

    def save(self):
        for case in self.cases:
            with open(self.dir / (case.ref + '.txt'), 'w') as f:
                print('Saved cases to ', self.dir)
                f.write(case.text_area.text)


if __name__ == "__main__":
    app = HelperApp()
    try:
        app.run()
    finally:
        app.save()

    if DEBUG:
        with open('~/Documents/deleteme_log.txt') as f:
            _print(f.read())
