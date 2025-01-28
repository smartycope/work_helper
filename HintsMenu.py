from textual.containers import *
from textual.widgets import *
from Menu import Menu

class HintsMenu(Menu):
    # require_case = False

    def compose(self):
        tree: Tree[str] = Tree("Hints", id='hints-tree')
        tree.root.expand()
        tree.show_root = False

        branch = tree.root.add('Trouble Emptying the Bin')
        branch.add_leaf('Factory Reset')
        branch.add_leaf('Clean IR sensors for the bot and bin')

        branch = tree.root.add('No/Low Audio')
        branch.add_leaf('Factory reset')
        branch.add_leaf('Ask Michelle or Penny before sending swap request')

        tree.focus()
        yield tree
        yield Button('Close', action='close')
