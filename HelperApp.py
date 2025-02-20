import datetime
import json
import random
from pathlib import Path

from textual.app import App, ComposeResult
from textual import on
from textual.containers import *
from textual.widgets import *
from CustomTextArea import CustomTextArea
from Phase import Phase
from Case import Case
from globals import COLORS, INTERNAL_LOG_PATH, SAVE_CASE_PATH, SAVE_STATE_PATH, EXISTING_CASES
from clipboard import copy, paste

from hotkeys import open_board, open_return_product, open_ship_product, query_case
from texts import Steps
import traceback

# {"notes": "19000IR\\n", "color": "#377a11", "ref": "19000IR", "serial": null, "phase": 0, "step": "Put labels on everything", "todo": ""}, {"notes": "19002IR\\nParts in: Robot\\nClaimed Damage: Minor scratches\\nVisible Damage: Confirmed claimed damage\\nCustomer States: Waaaaaa\\n\\nRoutine Checks:\\n* Contacts don't feel sunken\\n* No signs of liquid damage\\n* No play in blower motor\\n* Cleaned robot\\n! Robot does not charge on test base @ ~0W\\n\\nProcess:\\n* Step\\n* Step\\n* Step\\n* Done\\n", "color": "#d1dd0b", "ref": "19002IR", "serial": "i3", "phase": 3, "step": "All screws are screwed in all the way [done]", "todo": ""}, {"notes": "19003IR\\nParts in: Robot\\nClaimed Damage: Minor scratches\\nVisible Damage: Confirmed claimed damage\\nCustomer States: I want money back\\n\\nRoutine Checks:\\n* Contacts don't feel sunken\\n* No signs of liquid damage\\n* No play in blower motor\\n* Cleaned robot\\n* Robot charges on test base @ ~9W (battery is full)\\n\\nProcess:\\n* Tehe\\n* Swap\\n", "color": "#ea9daf", "ref": "19003IR", "serial": "j7", "phase": 4, "step": "Send swap email [confirmed]", "todo": ""}, {"notes": "19004IR\\nParts in: Robot\\nClaimed Damage: Minor scratches\\nVisible Damage: Confirmed claimed damage\\nCustomer States: It broke\\n\\nRoutine Checks:\\n* Contacts don't feel sunken\\n* No play in blower motor\\n* Tank float screw has no signs of rust\\n* Cleaned robot\\n* Robot charges on test base @ ~21W\\n\\nProcess:\\n* Step1\\n* Step2\\n", "color": "#799fad", "ref": "19004IR", "serial": "c9", "phase": 2, "step": "Add Step", "todo": ""}, {"notes": "new\\n", "color": "#ef9e16", "ref": "new", "serial": null, "phase": 0, "step": "Confirm IDs", "todo": ""}




DEBUG_STATE = '''["19002IR", "19003IR", "19004IR"]'''
DEBUG_CASES = {
    '19002IR': {"notes": "19002IR\nParts in: Robot\nClaimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\nCustomer States: Waaaaaa\n\nRoutine Checks:\n* Contacts don't feel sunken\n* No signs of liquid damage\n* No play in blower motor\n* Cleaned robot\n! Robot does not charge on test base @ ~0W\n\nProcess:\n* Step\n* Step\n* Step\n* Done\n\nCONTEXT:\n\n", "color": "#377a11", "ref": "19002IR", "serials": ["i3"], "phase": 0, "step": "Go pick up the case on CSS {case ID} [done]", "todo": "todo!"},
    '19003IR': {"notes": "19003IR\nParts in: Robot\nClaimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\nCustomer States: Waaaaaa\n\nRoutine Checks:\n* Contacts don't feel sunken\n* No signs of liquid damage\n* No play in blower motor\n* Cleaned robot\n! Robot does not charge on test base @ ~0W\n\nProcess:\n* Step\n* Step\n* Step\n* Done\n\nCONTEXT:\n\n", "color": "#ef9e16", "ref": "19003IR", "serials": ["m6"], "phase": Phase.DEBUGGING.value, "step": Steps.add_step, "todo": ""},
    '19004IR': {"notes": "19004IR\nParts in: Robot\nClaimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\nCustomer States: Waaaaaa\n\nRoutine Checks:\n* Contacts don't feel sunken\n* No signs of liquid damage\n* No play in blower motor\n* Cleaned robot\n! Robot does not charge on test base @ ~0W\n\nProcess:\n* Step\n* Step\n* Step\n* Done\n\nCONTEXT:\n\n", "color": "#d1dd0b", "ref": "19004IR", "serials": ["c9"], "phase": Phase.FINISH.value, "step": "Pass mobility and attempted BiT [done]", "todo": ""},
}


class HelperApp(App):
    BINDINGS = [
        # The visible ones
        Binding('ctrl+e', 'open_external_notes_menu', 'External notes', priority=True, system=True),
        Binding('ctrl+t', 'open_mobility_menu', 'Mobility Test', priority=True, system=True),

        # TODO
        # Binding('ctrl+b', 'open_board', 'Board', priority=True, system=True),
        # Binding('ctrl+p', 'query_case', 'Pickup', priority=True, system=True),
        # Binding('ctrl+r', 'open_return_product', 'Return', priority=True, system=True),
        # Binding('ctrl+f', 'open_ship_product', 'Ship', priority=True, system=True),

        Binding("ctrl+n", "new_case", "New Case", show=False, system=True, priority=True),
        Binding("ctrl+w", "close_case", "Close Case", show=False, system=True, priority=True),
        Binding("ctrl+s", "save", "Save", show=False, system=True, priority=True),

        Binding("ctrl+`,ctrl+g", "focus_input", "Focus Input", show=False, system=True, priority=True),
        # ('ctrl+e', 'open_external_notes_menu', 'Ext Notes'),
        # Binding('ctrl+1,ctrl+shift+1', 'goto_tab(1)', 'Tab 1', show=False, system=True, priority=True),
        # Binding('ctrl+2,ctrl+shift+2', 'goto_tab(2)', 'Tab 2', show=False, system=True, priority=True),
        # Binding('ctrl+3,ctrl+shift+3', 'goto_tab(3)', 'Tab 3', show=False, system=True, priority=True),
        # Binding('ctrl+4,ctrl+shift+4', 'goto_tab(4)', 'Tab 4', show=False, system=True, priority=True),
        # Binding('ctrl+5,ctrl+shift+5', 'goto_tab(5)', 'Tab 5', show=False, system=True, priority=True),

        Binding('ctrl+j', 'increment_tab', 'Next Tab', show=True, priority=True, system=True),
        Binding('ctrl+f', 'increment_tab(-1)', 'Previous Tab', show=True, priority=True, system=True),
    ]
    CSS_PATH = "stylesheet.tcss"
    COMMAND_PALETTE_DISPLAY = False
    ESCAPE_TO_MINIMIZE = False

    def __init__(self, debug=False):
        super().__init__()
        self._debug = debug
        self.cases = []
        self.tabs = TabbedContent(id='tabs')
        self.tabs.can_focus = False
        self.popup = Input(placeholder='Case ID (preface with "overwrite" to forcibly not load the case)', id='reference_popup')
        self.popup.visible = False

        self.menu_menu = Select(((m, m) for m in (
            'Hints',
            'Commands',
            'Acronyms',
            '----------------------',
            'Update Sidebar',
            "Remove Double Lines",
            '----------------------',
            "Copy Cases",
            "Paste Cases",
            "Load Saved State",
        )), id='menu-select', prompt='☰')
        self.menu_menu.can_focus = False

    def on_mount(self):
        if self._debug:
            for ref, data in DEBUG_CASES.items():
                with open(EXISTING_CASES[ref], 'w') as f:
                    json.dump(data, f)
            self.deserialize(DEBUG_STATE)
        else:
            self.action_load_saved_state()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Label(str(datetime.datetime.now().day), id='version')
        yield self.menu_menu
        yield self.tabs
        yield self.popup
        yield Footer()

    @on(Select.Changed, "#menu-select")
    def menu_menu_option_pressed(self, event):
        match event.value:
            case "Copy Cases":
                self.action_copy_all_cases()
            case "Paste Cases":
                self.action_add_cases_from_clipboard()
            case "Load Saved State":
                self.action_load_saved_state()
            case _:
                if self.active_case:
                    self.active_case.open_menu(event)
        event.control.clear()

    def action_open_mobility_menu(self):
        self.active_case.action_open_mobility_menu()

    def action_open_external_notes_menu(self):
        self.active_case.action_open_external_notes_menu()

    def key_escape(self):
        if self.popup.visible:
            self.popup.visible = False

    def _create_case(self, ref_or_case:str|Case, add_to_cases=True):
        """ May throw an error (since instantiating a case may throw an error) """
        if isinstance(ref_or_case, str):
            unused_color = random.choice(list(set(COLORS.keys()) - {i.color for i in self.cases}))
            # If we can't create a case (like, if there's a space in the ID somehow or something), just don't make one
            case = Case(ref_or_case, unused_color)
        elif isinstance(ref_or_case, Case):
            case= ref_or_case
        else:
            raise TypeError('Must be given a ref string or an instantiated case')

        if add_to_cases:
            self.cases.append(case)
        self.tabs.add_pane(TabPane('', case, id=f'tab-pane-{case.ref}'))
        self.action_save()

    # This actually creates the new case
    def on_input_submitted(self):
        # This should be the only way cases get deployed
        if self.popup.visible:
            self.popup.visible = False
            ref = self.popup.value
            self.popup.value = ''
            overwrite = False
            # If we get "overwite 19000ir", then don't deserialize the case
            if ' ' in ref:
                try:
                    a, b = ref.split(' ')
                    if a.lower() == 'overwrite':
                        ref = b
                        overwrite = True
                    else:
                        return
                except:
                    return
            if len(self.cases) < 5:
                try:
                    if overwrite or self._debug:
                        self._create_case(ref)
                    else:
                        self._create_case(Case.attempt_load_case(ref))
                except Exception as err:
                    if self._debug:
                        raise err
                    return

    def action_new_case(self):
        """Add a new tab."""
        self.popup.visible = True
        self.popup.focus()

    def action_close_case(self):
        self.action_save()
        # Only close the case if we're in the final phase or the hold phase
        # The extra clause here is in some weird deserializing situations
        if self.active_case.phase in (Phase.FINISH, Phase.HOLD) and self.active_case in self.cases:
            self.cases.remove(self.active_case)
            self.tabs.remove_pane(self.tabs.active_pane.id)
        self.action_save()

    @on(TabbedContent.TabActivated)
    def action_focus_input(self):
        if self.active_case:
            self.active_case.input.focus()

    @property
    def active_case(self):
        try:
            return self.tabs.active_pane.children[0]
        except AttributeError:
            return

    def action_remove(self) -> None:
        """Remove active tab."""
        active_tab = tabs.active_tab
        if active_tab is not None:
            self.action_save()
            self.cases.remove(self.active_case)
            self.tabs.remove_tab(active_tab.id)

    def action_copy_all_cases(self):
        copy(self.serialize())

    def action_add_cases_from_clipboard(self):
        self.deserialize(paste())

    def action_load_saved_state(self):
        try:
            with open(SAVE_STATE_PATH, 'r') as f:
                self.deserialize(f.read(), clear=True)
        except:
            pass

    def action_increment_tab(self, inc=1):
        try:
            idx = self.cases.index(self.active_case)
            next = self.cases[(idx + inc)%len(self.cases)]
            self.tabs.active = f'tab-pane-{next.ref}'
        # That tab (somehow) doesn't exist. Don't hold it against it.
        except ValueError:
            pass

    def serialize(self):
        return json.dumps([case.ref for case in self.cases])

    def deserialize(self, string, clear=False):
        """ If clear, it clears all the current cases before adding the new ones """
        try:
            new_cases = [Case.attempt_load_case(ref) for ref in json.loads(string)]
        except Exception as err:
            if self._debug:
                raise err
            else:
                return

        if clear:
            self.tabs.clear_panes()

        for case in new_cases:
            self._create_case(case)
            # self.tabs.add_pane(TabPane('', case, id=f'tab-pane-{case.ref}'))

    def action_goto_tab(self, index):
        self.bell()
        self.tabs.active = f'tab-{index}'

    def action_save(self):
        for case in self.cases:
            try: case.save()
            except: pass

        # Save the current state, as a backup
        with open(SAVE_STATE_PATH, 'w') as f:
            f.write(self.serialize())

    def action_open_board(self):
        open_board(self.active_case.ref)

    def action_open_ship_product(self):
        open_ship_product(self.active_case.ref)

    def action_open_return_product(self):
        open_return_product(self.active_case.ref)

    def action_query_case(self):
        query_case(self.active_case.ref)

    def panic(self, err):
        """ An error has occurred, and we need to save and clean up as best we can
        """
        try:
            with open(INTERNAL_LOG_PATH, 'a') as f:
                f.write(traceback.format_exc())
        except:
            pass

        try: self.action_save()
        except: pass

        if not self._debug:
            for case in self.cases:
                # Assume nothing! We're panicking!
                try:
                    print('\n')
                    print(case.ref, ':', sep='')
                    print('Serials, in order:')
                    print('\n'.join(case.serials))
                    print()
                    print('TODO:')
                    print(case.sidebar.todo.text)
                    print()
                    print('Notes:')
                    print(case.text_area.text)
                    print('-'*50)
                    print()
                except: pass
