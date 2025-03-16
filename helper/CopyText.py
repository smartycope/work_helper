from textual.containers import *
from textual.widgets import *
import clipboard


class CopyText(Static, can_focus=True):
    """A simple, clickable link that opens a URL."""

    DEFAULT_CSS = """
    CopyText {
        width: auto;
        height: auto;
        min-height: 1;
        color: $accent;
        # text-style: underline;
        background: $surface;
        &:hover { background: $surface-lighten-1; }
        &:focus { text-style: bold reverse; }
    }
    """

    BINDINGS = [Binding("enter", "copy", "Copy Text")]

    text: reactive[str] = reactive("", layout=True)
    to_copy: reactive[str] = reactive("")

    def __init__(
        self,
        text: str,
        to_copy: str | None = ...,
        *,
        tooltip: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            text, name=name, id=id, classes=classes, disabled=disabled, markup=False
        )
        # In this application specifically, this should always be the case
        self.can_focus = False
        self.set_reactive(CopyText.text, text)
        self.set_reactive(CopyText.to_copy, text if to_copy is Ellipsis else to_copy)
        self.tooltip = tooltip

    def watch_text(self, text: str) -> None:
        self.update(text)

    def on_click(self) -> None:
        self.action_copy()

    def action_copy(self) -> None:
        if self.to_copy is not None:
            clipboard.copy(self.to_copy)
