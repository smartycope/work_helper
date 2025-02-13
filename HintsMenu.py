from textual.containers import *
from textual.widgets import *
from Menu import Menu
import json
from pathlib import Path

with open(Path(__file__).resolve().parent / 'hints.json', 'r') as f:
    HINT_DATA = json.load(f)

class HintsMenu(Menu):
    def compose(self):


        tree: Tree[str] = Tree("Hints", id='hints-tree')
        tree.root.expand()
        tree.show_root = False

        def add_branch(parent, data):
            for key, value in data.items():
                if isinstance(value, dict):
                    branch = parent.add(key)
                    add_branch(branch, value)
                else:
                    for i in value:
                        parent.add_leaf(i)

        add_branch(tree.root, HINT_DATA)

        tree.focus()
        yield tree
        yield Button('Close', action='close')
