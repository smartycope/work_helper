from textual.containers import *
from textual.widgets import *
from Menu import Menu

class CommandsMenu(Menu):
    require_case = False

    def compose(self):
        yield Markdown("""\
`b|batt x [y]` -> Battery test x% / y[100]%

`fr` -> Factory reset

`s|sr` -> Swapped robot

`sd` -> swapped dock

`ar` -> Aurora refill debug steps

`hr` -> Hard reset

`hfr` -> Hard factory reset

`bit [args]` -> BiT: args[pass]

`bbk [args]` -> BBK: args[pass]

`ms|meas r/l [measurements]` -> Measured Right/Left contact: [avg]mm +/- [std]
        """)
        yield Button('Close', action='close')
