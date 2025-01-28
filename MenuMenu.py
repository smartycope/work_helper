from textual.containers import *
from textual.widgets import *
from Menu import Menu

class MenuMenu(Menu):
    require_case = False

    def compose(self):
        yield Button('Hints', id='hints-button')
        yield Button('Update Sidebar', id='update-sidebar-button')
