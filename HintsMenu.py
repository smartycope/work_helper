from textual.containers import *
from textual.widgets import *
from Menu import Menu

class HintsMenu(Menu):
    # require_case = False

    def compose(self):
        tree: Tree[str] = Tree("Hints", id='hints-tree')
        tree.root.expand()
        tree.show_root = False

        branch = tree.root.add('No/Low Audio')
        branch.add_leaf('Factory reset')
        branch.add_leaf('Ask Michelle or Penny before sending swap request')

        branch = tree.root.add('Pad not deploying')
        branch.add_leaf('Blow out chirp sensors')
        branch.add_leaf('Check there\'s water in the bin')
        branch.add_leaf('Test pad/Test bin')
        branch.add_leaf('If it fails with both a test pad and a test bin, and chirp sensors are blown out, it\'s a swap')
        branch.add_leaf('Factory reset')

        branch = tree.root.add('Evac Issues')
        branch.add_leaf('Factory Reset')
        branch.add_leaf('Clean IR sensors for the bot and bin')
        branch.add_leaf("Try swapping the CHM")
        branch.add_leaf("Check for a clog")
        branch.add_leaf("Try a new bin")
        branch.add_leaf("Try a new filter")


        tree.focus()
        yield tree
        yield Button('Close', action='close')
