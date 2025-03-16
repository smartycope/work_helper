import re

from textual.containers import *
from textual.widgets import *
from textual import on
from textual.events import Focus
from textual.message import Message

class CustomTextArea(TextArea):
    # Modified from https://textual.textualize.io/widgets/text_area/#textual.widgets._text_area.TextArea.BINDINGS
    # TODO: most of these don't seem to work (anything with alt seems to get intercepted by Konsole)
    BINDINGS = [
        Binding("up,alt+k", "cursor_up", "Cursor up", show=False),
        Binding("down,alt+l", "cursor_down", "Cursor down", show=False),
        Binding("left,alt+j", "cursor_left", "Cursor left", show=False),
        Binding("right,alt+;", "cursor_right", "Cursor right", show=False),
        Binding("ctrl+left,ctrl+alt+j", "cursor_word_left", "Cursor word left", show=False),
        Binding("ctrl+right,ctrl+alt+;", "cursor_word_right", "Cursor word right", show=False),
        Binding("ctrl+home,ctrl+alt+h,shift+home","cursor_document_start","Cursor beginning",show=False),
        Binding("ctrl+end,ctrl+alt+',shift+end", "cursor_document_end", "Cursor end", show=False),
        Binding("home,alt+h","cursor_line_start","Cursor line start",show=False),
        Binding("end,alt+'", "cursor_line_end", "Cursor line end", show=False),
        Binding("pageup", "cursor_page_up", "Cursor page up", show=False),
        Binding("pagedown", "cursor_page_down", "Cursor page down", show=False),
        Binding("ctrl+shift+left,ctrl+shift+alt+j", "cursor_word_left(True)", "Cursor left word select", show=False),
        Binding("ctrl+shift+right,ctrl+shift+alt+;", "cursor_word_right(True)", "Cursor right word select", show=False),
        Binding("shift+home,shfit+alt+h", "cursor_line_start(True)", "Cursor line start select", show=False),
        Binding("shift+end,shfit+alt+'", "cursor_line_end(True)", "Cursor line end select", show=False),
        Binding("shift+up,shift+alt+k", "cursor_up(True)", "Cursor up select", show=False),
        Binding("shift+down,shift+alt+l", "cursor_down(True)", "Cursor down select", show=False),
        Binding("shift+left,shift+alt+j", "cursor_left(True)", "Cursor left select", show=False),
        Binding("shift+right,shift+alt+;", "cursor_right(True)", "Cursor right select", show=False),
        Binding("ctrl+l", "select_line", "Select line", show=False),
        Binding("backspace", "delete_left", "Delete character left", show=False),
        Binding("ctrl+x", "cut", "Cut", show=False),
        Binding("ctrl+c", "copy", "Copy", show=False),
        Binding("ctrl+v", "paste", "Paste", show=False),
        # Binding("ctrl+u", "delete_to_start_of_line", "Delete to line start", show=False),
        # Binding("ctrl+k", "delete_to_end_of_line_or_delete_line", "Delete to line end", show=False),
        Binding("ctrl+shift+d", "delete_line", "Delete line", show=False),
        Binding("ctrl+z", "undo", "Undo", show=False),
        Binding("ctrl+y,ctrl+shift+z", "redo", "Redo", show=False),
        Binding('ctrl+a', 'select_all', 'Select All', show=False),
        Binding('esc', 'blur', 'Unfocus', show=False),
        Binding("shift+backspace,ctrl+backspace", "delete_word_left", "Delete left to start of word", show=False),
        Binding("delete", "delete_right", "Delete character right", show=False),
        Binding("ctrl+delete,ctrl+shift+backspace", "delete_word_right", "Delete right to start of word", show=False),
        # Binding('ctrl+m', 'open_mobility_menu', 'Open Mobility Menu'),
    ]

    def __init__(self, ref):
        super().__init__(ref + '\n', id='textarea_' + ref)
        self.cursor_blink = False

    def action_open_mobility_menu(self):
        self.post_message(self.OpenMobilityMenu())

    def cursor_document_start(self):
        self.move_cursor((0, 0), select=False)

    def cursor_document_end(self):
        self.move_cursor(self.document.end, select=False)

    @on(Focus)
    def on_focus(self):
        self.move_cursor(self.document.end, select=False)
