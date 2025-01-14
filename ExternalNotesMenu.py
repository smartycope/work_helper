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
        ("Rusty bin", "Recommend only using OEM cleaning products, as some products can rust components"),
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

    def __init__(self, case):
        super().__init__(classes='external-menu', id=f'external-menu-{case.ref}')
        self.visible = False
        self.case = case
        self.text = Label('', id='external-preview')

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

    def watch_visible(self):
        self.set_default_selections()

    def compose(self):
        self.selection = SelectionList(*list(zip(self.notes.keys(), range(len(self.notes)))))
        yield self.selection
        yield Static()
        yield self.text
        yield Static()
        with HorizontalGroup():
            yield Button('Close', id='close-external-notes')
            yield Button('Copy', id='copy-external-notes')

    def get_notes(self):
        return '. '.join(list(self.notes.values())[i] for i in sorted(self.selection.selected)) + '.'

    @on(Mount)
    @on(SelectionList.SelectedChanged)
    def update_selected_view(self) -> None:
        self.text.update(textwrap.fill(self.get_notes(), 50))

    @on(Button.Pressed, '#copy-external-notes')
    def copy(self):
        copy(self.get_notes())

    @on(Button.Pressed, '#close-external-notes')
    def close(self):
        self.visible = False
