from textual.containers import *
from textual.widgets import *
from textual import on
from textual.events import Mount
from textual.widgets.selection_list import Selection
from clipboard import copy
import textwrap

class ExternalNotesMenu(VerticalGroup):

    # These are in the order they should be in in the final notes
    notes = [
        "Replaced robot with equivalent model",
        "Replaced dock with equivalent model",
        "Recommend regular cleaning and maintenance",
        "Recommend regular cleaning of dock charging contacts",
        "Recommend regular cleaning of the bin filter",
        "Recommend using only OEM replacement bags",
        "Please place robot on dock to wake from shipping mode",
        "Remove yellow slip underneath robot once received to activate",
        "Factory reset performed, recommend re-provisioning robot on app",
        #J7's, if a swap (due to the client's dock might have outdated firmware):
        "Please provision robot to application",
    ]

    def __init__(self, case):
        super().__init__(classes='external-menu', id=f'external-menu-{case.ref}')
        self.visible = False
        self.case = case
        self.text = Label('', id='external-preview')

    def compose(self):
        notes = self.case.text_area.text.lower()

        try:
            old_battery = self.case.serial.startswith('r')
        except:
            old_battery = False

        self.selection = SelectionList[str](
            # Display name, index in notes/order, default state
            ("Replaced robot", 0),
            ("Replaced dock", 1),
            ("Recommend cleaning", 2),
            ("Recommend cleaning dock charging contacts", 3),
            ("Recommend cleaning filter", 4),
            ("Use correct bags", 5),
            ("Wake from shipping mode", 6, not old_battery),
            ("Remove battery strip", 7, old_battery),
            ("Factory reset", 8, 'factory reset' in notes),
            ("J7 and a swap", 9),
        )
        yield self.selection
        yield Static()
        yield self.text
        yield Static()
        with HorizontalGroup():
            yield Button('Close', id='close-external-notes')
            yield Button('Copy', id='copy-external-notes')

    def get_notes(self):
        return '. '.join(self.notes[i] for i in sorted(self.selection.selected)) + '.'

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
