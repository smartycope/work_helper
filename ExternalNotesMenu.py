import re
from typing import OrderedDict
from textual.containers import *
from textual.widgets import *
from textual import on
from textual.events import Mount
from clipboard import copy
import textwrap
from Menu import Menu
from multi_paste import multi_paste

class ExternalNotesMenu(Menu):
    # These are in the order they should be in in the final notes
    notes = OrderedDict((
        ("Replaced robot", "Replaced robot with equivalent model"),
        ("Replaced dock", "Replaced dock with equivalent model"),
        ("Recommend cleaning", "Recommend regular cleaning and maintenance"),
        ("Recommend cleaning dock charging contacts", "Recommend regular cleaning of dock charging contacts"),
        ("Recommend cleaning filter", "Recommend regular cleaning of the bin filter"),
        ("Use correct bags", "Recommend using only OEM replacement bags"),
        # auto-change this to exclude Bona if robot is a C10 (C10's can't use Bona)
        ("Rusty bin screw", "Recommend only using water, Bona, or iRobot cleaning solution, as other products can rust components"),
        ("Liquid spill", "Robot is not rated for liquid cleanup"),
        ("Broken mop pad", "Recommend hand washing mop pads, as machine wash can break them"),
        ("The Glitch", "If issues persist, factory reset as necessary"),
        ("Factory reset", "Factory reset performed, recommend re-provisioning robot on app"),
        ("Factory reset and Lapis bin", "Factory reset performed, recommend re-provisioning the robot and mop bin in the app"),
        ("Had child lock", "Child & pet lock removed, use app to re-enable"),
        ("Wake from shipping mode", "Please place robot on dock to wake from shipping mode"),
        ("Remove battery strip", "Remove yellow slip underneath robot once received to activate"),
        #J7's, if a swap (due to the client's dock might have outdated firmware
        ("J7 and a swap", "Please provision robot to application"),
    ))

    # TODO: This doesn't work
    BINDINGS = [
        ('esc', 'close')
    ]

    def __init__(self, case):
        # super().__init__(classes='external-menu', id=f'external-menu-{case.ref}')
        super().__init__(case)
        self.text = Label('', id='external-preview')
        self.cx_states = Label('cx states:\n', id='cx-states')

    def compose(self):
        self.selection = SelectionList(*zip(self.notes.keys(), range(len(self.notes))))
        yield self.selection
        yield Static()
        yield self.text
        yield Static()
        with HorizontalGroup():
            yield Button('Close', id='close-external-notes')#, action='close')
            yield Button('Copy', id='copy-external-notes')#, action='copy')
            yield Button('Copy, then notes', id='copy-external-notes-and-notes')#, action='copy')
        yield Static()
        yield self.cx_states
        self.set_default_selections()

    def select(self, name):
        self.selection.select(list(self.notes.keys()).index(name))

    def action_toggle(self):
        super().action_toggle()
        self.set_default_selections()

    def action_open(self):
        super().action_open()
        self.set_default_selections()

    def set_default_selections(self):
        notes = self.case.text_area.text.lower()

        try:
            old_battery = self.case.serial.startswith(('r', 'e'))
        except:
            old_battery = False

        if old_battery:
            self.select("Remove battery strip")
        else:
            self.select("Wake from shipping mode")

        if 'factory reset' in notes and not self.case.is_swap:
            self.select("Factory reset")
            if self.case.has_lapis:
                self.select("Factory reset and Lapis bin")

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

        self.cx_states.update('cx states:\n' + self.case.customer_states)

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
            self.get_notes(),
            self.case.text_area.text,
        )

    @on(Button.Pressed, '#copy-external-notes')
    def action_copy(self):
        copy(self.get_notes())

    # I hate how this is necissary
    @on(Button.Pressed, '#close-external-notes')
    def close(self):
        self.action_close()
