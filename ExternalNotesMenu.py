import re
from collections import OrderedDict
from textual.containers import *
from textual.widgets import *
from textual import on
from textual.events import Mount
from clipboard import copy
import textwrap
from Menu import Menu
from multi_paste import multi_paste

class ExternalNotesMenu(Menu):
    # TODO: put this in a JSON file
    # These are in the order they should be in in the final notes
    notes = OrderedDict((
        ("Replaced robot", "Replaced robot with equivalent model"),
        ("Replaced dock", "Replaced dock with equivalent model"),
        ("Alex-Albany ship with sealing error", "The dock may occasionally generate false error messages. It has been thoroughly tested to ensure optimal compatibility with your Roomba. iRobot is aware of this issue and is actively working on a software update for resolution. For any further inquiries, please reach out to iRobot support"),
        ("Recommend cleaning", "Recommend regular cleaning and maintenance"),
        ("Recommend cleaning charging contacts", "Over time, debris can accumulate on the charging contacts of both the robot and dock, which may prevent charging and potentially cause damage. To help maintain optimal performance, we recommend cleaning these contacts regularly"),
        ("Recommend cleaning filter", "Recommend regular cleaning of the bin filter"),
        ("Long runtime", "The number of times the Roomba goes over an area can be set in the app under Product Settings > Cleaning Preferences > Cleaning Passes"),
        ("Charges normally caveat", "Robot charges normally on standard test equipment"),
        ("Use correct bags", "Recommend using only OEM replacement bags"),
        ("Place dock away from obstacles", "Recommend placing dock at least 1.5 feet away from obstacles on either side, and at least 4 feet away from stairs and any obstacles in front of the dock"),
        # auto-change this to exclude Bona if robot is a C10 (C10's can't use Bona)
        ("Rusty bin screw", "Recommend only using water, Bona, or iRobot cleaning solution, as other products can rust components"),
        ("Liquid spill", "Advise that robots are not rated for liquid cleanup"),
        ("Broken mop pad", "Recommend hand washing mop pads, as machine wash can break them"),
        ("Factory reset", "Factory reset performed, recommend re-provisioning robot on app"),
        # ("Factory reset and Lapis bin", "Factory reset performed, recommend re-provisioning the robot and mop bin in the app"),
        ("The Glitch", "If issues persist, factory reset as necessary"),
        ("Had child lock", "Child & pet lock removed, use app to re-enable"),
        ("Wake from shipping mode", "Please place robot on dock to wake from shipping mode"),
        ("Remove battery strip", "Remove yellow slip underneath robot once received to activate"),
        #J7's, if a swap (due to the client's dock might have outdated firmware)
        ("J7 and a swap", "Please provision robot to application"),
    ))

    # TODO: This doesn't work
    BINDINGS = [
        ('esc', 'close')
    ]

    require_case = False
    def __init__(self, case=None):
        super().__init__(case)
        self.text = Label('', id='external-preview')
        self.cx_states = Label('', id='cx-states')
        self.cx_dock = Label('', id='cx-dock-label')

    def compose(self):
        with ScrollableContainer():
            self.selection = SelectionList(*zip(self.notes.keys(), range(len(self.notes))))
            yield self.selection
            yield Static()
            yield self.text
            yield Static()
            with HorizontalGroup():
                yield Button('Close', id='close-external-notes')#, action='close')
                yield Button('Copy', id='copy-external-notes')#, action='copy')
                # If this is being used by SerialParser, this doesn't make sense
                if type(self.case) is not str and self.case:
                    yield Button('Copy notes, then this', id='copy-external-notes-and-notes')#, action='copy')
            if type(self.case) is not str and self.case:
                # with HorizontalGroup(id='cx-states-dock'):
                yield Static('[underline]Customer States:[/]')
                yield self.cx_states
                yield Static('[underline]Customer Dock:[/]')
                yield self.cx_dock

        self.set_default_selections()

    def select(self, name):
        # if name in self.notes.keys():
        try:
            self.selection.select(list(self.notes.keys()).index(name))
        except ValueError:
            pass

    def action_toggle(self):
        super().action_toggle()
        self.set_default_selections()

    def action_open(self):
        super().action_open()
        self.set_default_selections()

    def set_default_selections(self):
        """  Guess what notes we need to use based on the case notes
            This has gotten pretty good. There's a few tweaks, but it's about 80% right. I usually
            add text by hand though (this doesn't mention replacing parts for example, by intent)
        """

        try:
            if type(self.case) is str and self.case:
                old_battery = self.case.lower().startswith(('r', 'e'))
            elif self.case:
                old_battery = self.case.serial.lower().startswith(('r', 'e'))
            else:
                old_battery = False
        except:
            old_battery = False

        if old_battery:
            self.select("Remove battery strip")
        else:
            self.select("Wake from shipping mode")

        case = self.case
        if type(self.case) is not str and self.case:
            notes = self.case.text_area.text.lower()
            if 'factory reset' in notes and not self.case.is_swap:
                self.select("Factory reset")
                # if self.case.has_lapis:
                    # self.select("Factory reset and Lapis bin")

            if self.case.is_swap:
                self.select("Replaced robot")
                if self.case.serial.startswith('j7'):
                    self.select("J7 and a swap")

            if re.search(r'(?i)swap.+dock', notes):
                self.select("Replaced dock")

            if self.case._bin_screw_has_rust or self.case._dock_tank_screw_has_rust:
                self.select("Rusty bin screw")

            if self.case._liquid_found:
                self.select("Liquid spill")

            if 'glitch' in notes:
                self.select("The Glitch")

            if "cleaned dock charging contacts" in notes:
                self.select("Recommend cleaning charging contacts")

            self.cx_states.update(textwrap.fill(self.case.customer_states, 55))
            self.cx_dock.update(self.case.dock)

    def get_notes(self):
        indexes = self.selection.selected
        add_to_beginning = []
        add_to_end = []

        # Swapped both bot and dock
        if 0 in indexes and 1 in indexes:
            indexes.remove(0)
            indexes.remove(1)
            add_to_beginning.append("Replaced robot and dock with equivalent models")

        sentences = [list(self.notes.values())[i] for i in sorted(indexes)]

        return '. '.join(add_to_beginning + sentences + add_to_end) + '.'

    @on(Mount)
    @on(SelectionList.SelectedChanged)
    def update_selected_view(self) -> None:
        self.text.update(textwrap.fill(self.get_notes(), 60))

    @on(Button.Pressed, '#copy-external-notes-and-notes')
    def action_copy_both(self):
        multi_paste(
            self.case.text_area.text,
            self.get_notes(),
        )

    @on(Button.Pressed, '#copy-external-notes')
    def action_copy(self):
        copy(self.get_notes())

    # I hate how this is necissary, I don't know why it is
    @on(Button.Pressed, '#close-external-notes')
    def close(self):
        self.action_close()
