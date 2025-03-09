from textual.containers import *
from textual.widgets import *
from Menu import Menu
from parse_commands import ACRONYMS

class AcronymMenu(Menu):
    require_case = False

    def compose(self):
        s = "All acryonyms are case insensitve, and are applied when they're by themselves only\n\n"

        for acr, expanded in ACRONYMS.items():
            s += f'{acr} -> {expanded.replace("[", "\\[")}\n'

        yield ScrollableContainer(Static(s))
        yield Button('Close', action='close')
