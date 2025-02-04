from textual.containers import *
from textual.widgets import *
from Menu import Menu

class CommandsMenu(Menu):
    require_case = False

    def compose(self):
        yield Static("""\
All commands stick extra parameters at the end as notes
All commands are case insensitive

`b|batt <x> \[y]` -> Battery test x% / y\[100]%
`fr` -> Factory reset
`s|sr` -> Swapped robot
`sd` -> swapped dock
`ar` -> Aurora refill debug steps
`hr` -> Hard reset
`hfr` -> Hard factory reset
`bit \[args]` -> BiT: args\[pass]
`bbk \[args]` -> BBK: args\[pass]
`ms|meas r/l \[measurements]` -> Measured Right/Left contact: \[avg]mm +/- \[std]
'ms|meas` -> Measured both contacts: >4mm
`blew|chirp` -> Blew out chirp sensors
`cdc|cln` -> Cleaned dock charging contacts
`prov` -> Provisioned robot to the app
`fb` -> Freebee
`2xm` -> Double checked with Michelle
`cm` -> Confirmed with Michelle
        """)
# `ch|charge \[watts] (dock) (bot)` -> \[bot(Robot)] charges on \[dock (dock)] @ ~\[watts]W
        yield Button('Close', action='close')

# `diag` -> Diagnosis:
