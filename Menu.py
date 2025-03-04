from typing import OrderedDict
from textual.containers import *
from textual.widgets import *
from textual import on
from textual.events import Mount
from clipboard import copy
import textwrap


class Menu(VerticalGroup, can_focus=True):
    require_case = True

    def __init__(self, case=None, **kwargs):
        super().__init__(**kwargs)
        self.visible = False

        # If case is required but not provided, raise an error
        if self.require_case and case is None:
            raise ValueError(f"{self.__class__.__name__} requires a 'case' argument.")

        self.case = case

    def action_toggle(self):
        # self.visible = not self.visible
        # So any side effects get run as well
        if self.visible:
            self.action_close()
        else:
            self.action_open()

    def action_open(self):
        self.visible = True
        self.focus()

    def action_close(self):
        self.visible = False
