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
from globals import COLORS, DEFAULT_COLOR, INTERNAL_LOG_PATH, SAVE_CASE_PATH, SAVE_STATE_PATH, EXISTING_CASES
from clipboard import copy, paste

from hotkeys import open_board, open_board_dynamic, open_return_product, open_ship_product, query_case
import settings
from texts import Steps
import traceback
import shutil
import time


# TODO: move this into a seperate file
DEBUG_STATE = '''["19002IR", "19003IR", "19004IR"]'''
DEBUG_CASES = {
    '19002IR': {"notes": "19002IR\nParts in: Robot\nClaimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\nCustomer States: Waaaaaa\n\nRoutine Checks:\n* Contacts don't feel sunken\n* No signs of liquid damage\n* No play in blower motor\n* Cleaned robot\n! Robot does not charge on test base @ ~0W\n\nProcess:\n* Step\n* Step\n* Step\n* Done\n\nCONTEXT:\n\n", "color": "#377a11", "ref": "19002IR", "serials": ["i3"], "phase": 0, "step": "Go pick up the case on CSS {case ID} [done]", "todo": "todo!", "repeat": True, "adj": 10*60+27},
    '19004IR': {"notes": "19004IR\nParts in: Robot\nClaimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\nCustomer States: Waaaaaa\n\nRoutine Checks:\n* Contacts don't feel sunken\n* No signs of liquid damage\n* No play in blower motor\n* Cleaned robot\n! Robot does not charge on test base @ ~0W\n\nProcess:\n* Step\n* Step\n* Step\n* Done\n\nCONTEXT:\n\n", "color": "#d1dd0b", "ref": "19004IR", "serials": ["m6"], "phase": Phase.FINISH.value, "step": "Pass mobility and attempted BiT [done]", "todo": ""},
    '19003IR': {"notes": "19003IR\nParts in: Robot\nClaimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\nCustomer States: Waaaaaa\n\nRoutine Checks:\n* Contacts don't feel sunken\n* No signs of liquid damage\n* No play in blower motor\n* Cleaned robot\n! Robot does not charge on test base @ ~0W\n\nProcess:\n* Step\n* Step\n* Step\n* Done\n\nCONTEXT:\n\n", "color": "#ef9e16", "ref": "19003IR", "serials": ["c9"], "phase": Phase.DEBUGGING.value, "step": Steps.add_step, "todo": ""},
}

if settings.INCLUDE_HOTKEYS:
    HOTKEY_BINDINGS = [
        Binding('ctrl+b', 'open_board_dynamic', 'Board', priority=True, system=True, show=settings.SHOW_HOTKEYS),
        Binding('ctrl+p', 'query_case', 'Pickup', priority=True, system=True, show=settings.SHOW_HOTKEYS),
        Binding('ctrl+r', 'open_return_product', 'Return', priority=True, system=True, show=settings.SHOW_HOTKEYS),
        Binding('ctrl+f', 'open_ship_product', 'Ship', priority=True, system=True, show=settings.SHOW_HOTKEYS),
    ]
else:
    HOTKEY_BINDINGS = []


class HelperApp(App):
    BINDINGS = [
        # The visible ones
        Binding('ctrl+e', 'open_external_notes_menu', 'External notes', priority=True, system=True),
        Binding('ctrl+t', 'open_mobility_menu', 'Mobility Test', priority=True, system=True),
        # TODO
        Binding('ctrl+k', 'move_tab(1)', 'Move Tab Left', priority=True, system=True, show=False),
        Binding('ctrl+d', 'move_tab(-1)', 'Move Tab Right', priority=True, system=True, show=False),

        Binding("ctrl+n", "new_case", "New Case", show=False, system=True, priority=True),
        Binding("ctrl+w", "close_case", "Close Case", show=False, system=True, priority=True),
        Binding("ctrl+s", "save_manual", "Save", show=False, system=True, priority=True),

        Binding("ctrl+`,ctrl+g", "focus_input", "Focus Input", show=False, system=True, priority=True),

        Binding('ctrl+j', 'increment_tab', 'Next Tab', show=False, priority=True, system=True),
        Binding('ctrl+f', 'increment_tab(-1)', 'Previous Tab', show=False, priority=True, system=True),

        Binding('ctrl+l', 'toggle_lapis_qr', 'Lapis QR', show=True, priority=True, system=True),

    ] + HOTKEY_BINDINGS
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

        # The commented out options should still work, they're just not useful anymore
        self.menu_menu = Select(((m, m) for m in (
            'Hints',
            'Commands',
            'Acronyms',
            'Lapis QR',
            '----------------------',
            'Update Sidebar',
            "Remove Double Lines",
            # '----------------------',
            # "Copy Cases",
            # "Paste Cases",
            # "Load Saved State",
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

        self._save_timer = None
        if settings.SAVE_EVERY_MINUTES and settings.SAVE_EVERY_MINUTES > 0:
            self._save_timer = self.set_interval(settings.SAVE_EVERY_MINUTES*60, self.action_save)


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
        if self.active_case:
            self.active_case.action_open_mobility_menu()

    def action_open_external_notes_menu(self):
        if self.active_case:
            self.active_case.action_open_external_notes_menu()

    def key_escape(self):
        if self.popup.visible:
            self.popup.visible = False

    def _create_case(self, ref_or_case:str|Case, add_to_cases=True):
        """ May throw an error (since instantiating a case may throw an error) """
        if isinstance(ref_or_case, str):
            if len(self.cases) < len(COLORS):
                color = random.choice(list(set(COLORS.keys()) - {i.color for i in self.cases}))
            else:
                color = DEFAULT_COLOR
            # If we can't create a case (like, if there's a space in the ID somehow or something), just don't make one
            case = Case(ref_or_case, color)
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

    @on(Case.CloseCaseMessage)
    def action_close_case(self):
        if self.active_case:
            self.action_save()
            self.active_case.log('close')
            # Only close the case if we're in the final phase or the hold phase
            # The extra clause here is in some weird deserializing situations
            # if self.active_case.phase in (Phase.FINISH, Phase.HOLD) and self.active_case in self.cases:
            if (self.active_case.phase in (Phase.FINISH, Phase.HOLD) or not settings.RESTRICT_CLOSING_SHORTCUT) and self.active_case in self.cases:
                self.cases.remove(self.active_case)
                self.tabs.remove_pane(self.tabs.active_pane.id)
            self.action_save()

    @on(TabbedContent.TabActivated)
    def action_focus_input(self):
        if self.active_case:
            self.active_case.input.focus()

    @property
    def active_case(self) -> Case:
        try:
            return self.tabs.active_pane.children[0]
        except (AttributeError, IndexError):
            return

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
        if self.active_case:
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

    async def action_move_tab(self, amt):
        if self.active_case:
            case: Case = self.active_case
            idx = self.cases.index(case)
            new_idx = (idx + amt) % len(self.cases)

            # Modify self.cases
            self.cases.insert(new_idx, self.cases.pop(idx))

            # Calculate the pane it should be before
            before_pane = f'tab-pane-{self.cases[new_idx+1].ref}' if new_idx < len(self.cases) - 1 else None

            # Remove the current pane, and add it back into the correct place
            active_pane = f'tab-pane-{case.ref}'
            # pane = self.tabs.get_pane(active_pane)
            await self.tabs.remove_pane(active_pane)
            # case = pane.children[0]
            # await self.tabs.add_pane(TabPane('', case, id=f'tab-pane-{case.ref}'), before=before_pane)
            pane = TabPane('', case, id=f'tab-pane-{case.ref}')
            await self.tabs.add_pane(pane, before=before_pane)

            # Bugfix, unsure why it's needed
            case.mobility_menu.setup()

            # Re-set the color, because the tab colors are set dynamically, and this is technically
            # an entierly new tab
            to_color = case.color
            case.sidebar.color_switcher.value = DEFAULT_COLOR
            case.sidebar.color_switcher.value = to_color

            # This is copied from case.set_color()
            # TODO: This works, but the color switcher box gets unset, just like the phase box does
            # on deserialization. Once I figure that out, fix it here too
            case.sidebar.styles.background = to_color
            case._tab.styles.background = to_color
            case._tab.styles.color = 'black'
            self.tabs.active = active_pane

    def action_toggle_lapis_qr(self):
        if self.active_case:
            self.active_case.lapis_qr_menu.action_toggle()

    def action_save(self):
        for case in self.cases:
            try: case.save()
            except: pass

        # Save the current state, as a backup
        with open(SAVE_STATE_PATH, 'w') as f:
            f.write(self.serialize())

    def action_save_manual(self):
        self.action_save()
        # TODO: remove this try/except statement, I think it's uneccisary, I just don't trust my own code
        try:
            timestamp = time.strftime("%m-%d-%Y.%H:%M:%S")
            backup_path = SAVE_CASE_PATH.parent / f"{SAVE_CASE_PATH.name}_backup_{timestamp}"

            shutil.copytree(SAVE_CASE_PATH, backup_path)
        except: pass

    def action_open_board(self):
        if self.active_case:
            open_board(self.active_case.ref)

    def action_open_board_dynamic(self):
        if self.active_case:
            open_board_dynamic(self.active_case.ref)

    def action_open_ship_product(self):
        if self.active_case:
            open_ship_product(self.active_case.ref)

    def action_open_return_product(self):
        if self.active_case:
            open_return_product(self.active_case.ref)

    def action_query_case(self):
        if self.active_case:
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

        # We should be able to safely raise the error *after* we've printed everything
        # raise err
