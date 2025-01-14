from textual.containers import *
from textual.widgets import *

class CustomInput(Input):
    BINDINGS = (
        Binding('ctrl+a', 'select_all', 'Select All', show=False),
    )
