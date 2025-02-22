from textual.containers import *
from textual.widgets import *
from Menu import Menu

class CommandsMenu(Menu):
    require_case = False

    def compose(self):
        yield ScrollableContainer(Static("""\
All commands stick extra parameters at the end as notes
All commands are case insensitive

`batt <x> \[y]` -> Battery test x% / y\[100]%
`s|sr` -> Swapped robot
`sd` -> swapped dock
`ar` -> Aurora refill debug steps
`bit \[args]` -> BiT: args\[pass]
`bbk \[args]` -> BBK: args\[pass]
`meas r/l/b \[measurements]` -> Measured Right/Left contact: \[avg]mm +/- \[std]
'meas r/l/b` -> Measured right/left/both contact\[s]: >4mm
`blew chirp/cliff` -> Blew out chirp/cliff sensors
`cln` -> Cleaned dock charging contacts
`cln r` -> Cleaned robot charging contacts
`prov <app/lapis/both>` -> Provisioned robot to the app/Provisioned lapis bin on app
`reprov` -> Reprovisioned robot to the app
`2m` -> Double checked with Michelle
`cm` -> Confirmed with Michelle
`rm` -> Removed provisioning
`bump \[in/out\]` -> Cleaned <in/out> side of the bumper
`rp` -> Replaced
`am` -> Attempted mobility test:
`diag` -> Diagnosis:
`upfw` -> Update firmware
`nozzle` -> Cleaned out drip nozzles
"""))
# `ch|charge \[watts] (dock) (bot)` -> \[bot(Robot)] charges on \[dock (dock)] @ ~\[watts]W
        yield Button('Close', action='close')
