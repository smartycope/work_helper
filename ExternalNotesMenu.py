from textual.containers import *
from textual.widgets import *
from textual import on
from textual.events import Mount
from textual.widgets.selection_list import Selection


class ExternalNotesMenu(VerticalGroup):
    def __init__(self, case):
        super().__init__(classes='external-menu', id=f'external-menu-{case.ref}')
        self.visible = True
        self.case = case
        self.text = Label('')
        self.selection = SelectionList[str](
            Selection("Replaced robot", "Replaced robot with equivalent model. "),
            Selection("Replaced dock", "Replaced dock with equivalent model. "),
            Selection("Recommend cleaning", "Recommend regular cleaning and maintenance. "),
            Selection("Recommend cleaning dock charging contacts", "Recommend regular cleaning of dock charging contacts. "),
            Selection("Recommend cleaning filter", "Recommend regular cleaning of the bin filter. "),
            Selection("Use correct bags", "Recommend using only OEM replacement bags. "),
            Selection("Wake from shipping mode", "Please place robot on dock to wake from shipping mode. ", True),
            Selection("Remove battery strip", "Remove yellow slip underneath robot once received to activate. "),
            Selection("Factory reset", "Factory reset performed, recommend re-provisioning robot on app. "),
            #J7's, if a swap (due to the client's dock might have outdated firmware):
            Selection("J7 and a swap", "Please provision robot to application. "),
        )

    def compose(self):
        yield self.selection
        yield self.text
        with HorizontalGroup():
            yield Button('Close', id='close-external-notes')
            yield Button('Copy', id='copy-external-notes')

    # @on(Mount)
    @on(SelectionList.SelectedChanged)
    def update_selected_view(self) -> None:
        self.text.update("".join(self.selection.selected))

    @on(Button.Pressed, '#close-external-notes')
    def copy(self):
        copy(self.text.value)

    @on(Button.Pressed, '#copy-external-notes')
    def close(self):
        self.visible = False
