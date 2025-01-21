import json
import random
from pathlib import Path

from textual.app import App, ComposeResult
from textual import on
from textual.containers import *
from textual.widgets import *
from Phase import Phase
from Case import Case
from globals import COLORS
from clipboard import copy, paste

DEBUG_STATE = '''[{"notes": "19000IR\\n", "color": "#377a11", "ref": "19000IR", "serial": null, "phase": 0, "step": "Put labels on everything", "todo": ""}, {"notes": "19002IR\\nParts in: Robot\\nClaimed Damage: Minor scratches\\nVisible Damage: Confirmed claimed damage\\nCustomer States: Waaaaaa\\n\\nRoutine Checks:\\n* Contacts don't feel sunken\\n* No signs of liquid damage\\n* No play in blower motor\\n* Cleaned robot\\n! Robot does not charge on test base @ ~0W\\n\\nProcess:\\n* Step\\n* Step\\n* Step\\n* Done\\n", "color": "#d1dd0b", "ref": "19002IR", "serial": "i3", "phase": 3, "step": "All screws are screwed in all the way [done]", "todo": ""}, {"notes": "19003IR\\nParts in: Robot\\nClaimed Damage: Minor scratches\\nVisible Damage: Confirmed claimed damage\\nCustomer States: I want money back\\n\\nRoutine Checks:\\n* Contacts don't feel sunken\\n* No signs of liquid damage\\n* No play in blower motor\\n* Cleaned robot\\n* Robot charges on test base @ ~9W (battery is full)\\n\\nProcess:\\n* Tehe\\n* Swap\\n", "color": "#ea9daf", "ref": "19003IR", "serial": "j7", "phase": 4, "step": "Send swap email [confirmed]", "todo": ""}, {"notes": "19004IR\\nParts in: Robot\\nClaimed Damage: Minor scratches\\nVisible Damage: Confirmed claimed damage\\nCustomer States: It broke\\n\\nRoutine Checks:\\n* Contacts don't feel sunken\\n* No play in blower motor\\n* Tank float screw has no signs of rust\\n* Cleaned robot\\n* Robot charges on test base @ ~21W\\n\\nProcess:\\n* Step1\\n* Step2\\n", "color": "#799fad", "ref": "19004IR", "serial": "c9", "phase": 2, "step": "Add Step", "todo": ""}, {"notes": "new\\n", "color": "#ef9e16", "ref": "new", "serial": null, "phase": 0, "step": "Confirm IDs", "todo": ""}]'''

class HelperApp(App):
    BINDINGS = [
        Binding('ctrl+m', 'open_mobility_menu', 'Mobility', priority=True, system=True),
        Binding('ctrl+e', 'open_external_notes_menu', 'Ext notes', priority=True, system=True),
        Binding("ctrl+n", "new_case", "New Case", show=False, system=True, priority=True),
        Binding("ctrl+w", "close_case", "Close Case", show=False, system=True, priority=True),
        Binding("ctrl+s", "save", "Save", show=False, system=True, priority=True),
        # ('ctrl+e', 'open_external_notes_menu', 'Ext Notes'),
        Binding("__", "remove_double_lines", "rm double lines", key_display=''),
        Binding('_c', 'copy_all_cases', 'Copy Cases', key_display=''),
        Binding('_v', 'add_cases_from_clipboard', 'Paste Cases', key_display=''),
        Binding('ctrl+1,ctrl+shift+1', 'goto_tab(1)', 'Tab 1', show=False, system=True, priority=True),
        Binding('ctrl+2,ctrl+shift+2', 'goto_tab(2)', 'Tab 2', show=False, system=True, priority=True),
        Binding('ctrl+3,ctrl+shift+3', 'goto_tab(3)', 'Tab 3', show=False, system=True, priority=True),
        Binding('ctrl+4,ctrl+shift+4', 'goto_tab(4)', 'Tab 4', show=False, system=True, priority=True),
        Binding('ctrl+5,ctrl+shift+5', 'goto_tab(5)', 'Tab 5', show=False, system=True, priority=True),


        # Binding('ctrl+tab', 'next_tab', 'Next Tab', show=True, priority=True),
        # Binding('ctrl+shift+tab', 'prev_tab', 'Previous Tab', show=True, priority=True),
    ]
    CSS_PATH = "stylesheet.tcss"
    COMMAND_PALETTE_DISPLAY = False
    ESCAPE_TO_MINIMIZE = False

    def __init__(self, debug=False):
        super().__init__()
        self._debug = debug
        self.cases = []
        self.dir = Path.home() / 'Documents' / 'Case_Notes'
        self.save_state_path = Path.home() / 'Documents' / 'helper_state.json'
        self.dir.mkdir(parents=True, exist_ok=True)

        self.tabs = TabbedContent(id='tabs')
        self.popup = Input(placeholder='Case ID', id='reference_popup')
        self.popup.visible = False

    def on_mount(self):
        if self._debug:
            self.deserialize(DEBUG_STATE)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield self.tabs
        yield self.popup
        yield Footer()

    def action_open_mobility_menu(self):
        self.active_case.action_open_mobility_menu()

    def action_open_external_notes_menu(self):
        self.active_case.action_open_external_notes_menu()

    def key_escape(self):
        if self.popup.visible:
            self.popup.visible = False

    def on_input_submitted(self):
        # This should be the only way cases get deployed
        if self.popup.visible:
            self.popup.visible = False
            ref = self.popup.value
            self.popup.value = ''
            if len(self.cases) < 5:
                unused_color = random.choice(list(set(COLORS.keys()) - {i.color for i in self.cases}))
                # If we can't create a case (like, if there's a space in the ID somehow or something), just don't make one
                try:
                    case = Case(ref, unused_color)
                except: return
                self.cases.append(case)
                # They're automatically id'd as tab-1, tab-2, ...
                # self.tabs.add_pane(TabPane(ref, case, id='pane-'+str(unused_color)))
                self.tabs.add_pane(TabPane(ref, case))

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

    @on(TabbedContent.TabActivated)
    def action_focus_input(self):
        self.active_case.input.focus()

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

    def action_copy_all_cases(self):
        copy(self.serialize())

    def action_add_cases_from_clipboard(self):
        self.deserialize(paste())

    # def next_tab(self):
        # # print('next tab called')
        # # print(f'active case:', self.active_case.ref)
        # idx = self.cases.index(self.active_case)
        # next = self.cases[(idx+1)%len(self.cases)]
        # print(f'next case:', next.ref)
        # self.tabs.active = f'pane-{next.color}'

    # def prev_tab(self):
        # # print('prev tab called')
        # idx = self.cases.index(self.active_case)
        # prev = self.cases[idx-1]
        # self.tabs.active = f'pane-{prev.color}'

    def serialize(self):
        return json.dumps([case.serialize() for case in self.cases])

    def deserialize(self, string, clear=False):
        """ If clear, it clears all the current cases before adding the new ones """
        try:
            self.cases = [Case.deserialize(case) for case in json.loads(string)]
        except Exception as err:
            if self._debug:
                raise err
            else:
                return

        if clear:
            self.clear_panes()

        for case in self.cases:
            self.tabs.add_pane(TabPane(case.ref, case))

    # def action_focus_input(self):
    #     self.active_case.input.focus()

    def action_goto_tab(self, index):
        self.bell()
        self.tabs.active = f'tab-{index}'

    def action_save(self):
        for case in self.cases:
            with open(self.dir / (case.ref + '.txt'), 'w') as f:
                print('Saved cases to ', self.dir)
                f.write(case.text_area.text)

        # Save the current state, as a backup
        with open(self.save_state_path, 'w') as f:
            f.write(self.serialize())

    def action_remove_double_lines(self):
        self.active_case.text_area.text = self.active_case.text_area.text.replace('\n\n', '\n')
