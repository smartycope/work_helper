from textual.containers import *
from textual.widgets import *
from Menu import Menu

class CommandsMenu(Menu):
    require_case = False

    def compose(self):
        yield Markdown("""\
`b|batt x y` -> Battery test x% / y%

`b|batt x` -> Battery test x%/100%

`fr` -> Factory reset

`s|sr` -> Swapped robot

`sd` -> swapped dock

`ar` -> Aurora refill debug steps
        """)
        yield Button('Close', action='close')
