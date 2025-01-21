from typing import OrderedDict
from textual.containers import *
from textual.widgets import *
from textual import on
from textual.events import Mount
from clipboard import copy
import textwrap

class ExternalNotesMenu(VerticalGroup):
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
        ("Broken mop pad", "Recommend hand washing mop pads"),
        ("Factory reset and Lapis bin", "Recommend re-provisioning the mop bin to the robot"),
        ("Factory reset", "Factory reset performed, recommend re-provisioning robot on app"),
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
        super().__init__(classes='external-menu', id=f'external-menu-{case.ref}')
        self.visible = False
        self.case = case
        self.text = Label('', id='external-preview')

    def select(self, name):
        self.selection.select(list(self.notes.keys()).index(name))

    def toggle(self):
        self.visible = not self.visible
        self.set_default_selections()

    def action_close(self):
        self.visible = False

    def set_default_selections(self):
        notes = self.case.text_area.text.lower()

        try:
            old_battery = self.case.serial.startswith('r')
        except:
            old_battery = False

        if old_battery:
            self.select("Remove battery strip")
        else:
            self.select("Wake from shipping mode")

        if 'factory reset' in notes:
            self.select("Factory reset")
            if self.case.has_lapis:
                self.select("Factory reset and Lapis bin")

        if 'swap' in notes:
            self.select("Replaced robot")
            if self.case.serial.startswith('j7'):
                self.select("J7 and a swap")

        if self.case._bin_screw_has_rust or self.case._dock_tank_screw_has_rust:
            self.select("Rusty bin screw")

        if self.case._liquid_found:
            self.select("Liquid spill")

    def compose(self):
        self.selection = SelectionList(*zip(self.notes.keys(), range(len(self.notes))))
        yield self.selection
        yield Static()
        yield self.text
        yield Static()
        with HorizontalGroup():
            yield Button('Close', id='close-external-notes')
            yield Button('Copy', id='copy-external-notes')
        self.set_default_selections()

    def get_notes(self):
        return '. '.join(list(self.notes.values())[i] for i in sorted(self.selection.selected)) + '.'

    @on(Mount)
    @on(SelectionList.SelectedChanged)
    def update_selected_view(self) -> None:
        self.text.update(textwrap.fill(self.get_notes(), 60))

    @on(Button.Pressed, '#copy-external-notes')
    def copy(self):
        copy(self.get_notes())

    @on(Button.Pressed, '#close-external-notes')
    def close(self):
        self.visible = False
