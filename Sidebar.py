import textwrap

from clipboard import copy
from textual.containers import *
from textual.reactive import reactive
from textual.widgets import *
from info import sleep_mode, factory_reset
from Phase import Phase
from globals import COLORS, SIDEBAR_WIDTH, COPY_SERIAL_BUTTON_WIDTH

class TodoTextArea(TextArea):
    BINDINGS = (
        Binding('ctrl+a', 'select_all', 'Select All', show=False),
    )

    def __init__(self, *a, **kw):
        super().__init__(*a, id='todo-textarea', **kw)
        self.cursor_blink = False


class Sidebar(VerticalGroup):
    serial = reactive('')

    def __init__(self, case):
        # super().__init__(id='sidebar-' + str(case.color))
        super().__init__(classes='sidebar', id='sidebar-' + case.ref)
        self.case = case
        self.styles.background = self.case.color
        self.todo = TodoTextArea()
        self.phase_selector = Select([(i.name, i.value) for i in Phase], id='phase-select', allow_blank=False)
        self.phase_selector.can_focus = False

    def watch_serial(self, *args):
        if self.serial:
            self.ref_model.update(f'{self.case.ref+" • "+self.case.get_quick_model():^{SIDEBAR_WIDTH}}\n')
            # self.model.update(f'{{:^{SIDEBAR_WIDTH}}}'.format(self.case.get_quick_model() + '\n'))
            self.sleep_mode.update(textwrap.fill(sleep_mode.get(self.serial[0], 'Unknown'), SIDEBAR_WIDTH) + '\n')
            self.factory_reset.update(textwrap.fill(factory_reset.get(self.serial[0], 'Unknown'), SIDEBAR_WIDTH) + '\n')
            self.dct.update(f'{{:^{SIDEBAR_WIDTH}}}'.format(textwrap.fill(self.case.get_DCT(), SIDEBAR_WIDTH)) + '\n')
            self.dct_exp.update(f'{{:^{SIDEBAR_WIDTH}}}'.format(textwrap.fill(self.case.get_DCT_exceptions(), SIDEBAR_WIDTH)) + '\n')
            self.serial_label.update(f'\n{self.serial.upper():^{SIDEBAR_WIDTH-COPY_SERIAL_BUTTON_WIDTH}}')
            # self.serial_label.update(self.serial)
            notes = textwrap.fill(self.case.get_notes(), SIDEBAR_WIDTH)
            if notes:
                self.notes_sep.update(f'{" Notes ":-^{SIDEBAR_WIDTH}}')
                self.notes.update(notes)

    def compose(self):
        self.color_switcher = Select(
            [(f'[{color}]{name}[/]', color) for color, name in COLORS.items()],
            id="color-selector",
            allow_blank=False,
            value=self.case.color,
        )
        # self.color_switcher.styles.margin = 0
        # self.color_switcher.styles.padding = 0
        # self.color_switcher.styles.height = 1
        # self.color_switcher.styles.background = list(COLORS.keys())[self.case.color]
        self.color_switcher.can_focus = False
        yield self.color_switcher

        self.ref_model = Label(f'{self.case.ref:^{SIDEBAR_WIDTH}}\n', id=f'ref-label-{self.case.ref}')
        yield self.ref_model
        with HorizontalGroup():
            # yield Label(f'{"Phase":^{SIDEBAR_WIDTH}}\n')
            yield Label("\nPhase: ")
            yield self.phase_selector
        yield Label('\n')
        # yield Label(f'{" Model ":-^{SIDEBAR_WIDTH}}')
        # self.model = Label('', id=f'model-label-{self.case.ref}')
        # yield self.model
        yield Label(f'{" Sleep Mode ":-^{SIDEBAR_WIDTH}}')
        self.sleep_mode = Label('', id=f'sleep-mode-label-{self.case.ref}')
        yield self.sleep_mode
        yield Label(f'{" Factory Reset ":-^{SIDEBAR_WIDTH}}')
        self.factory_reset = Label('', id=f'factory-reset-label-{self.case.ref}')
        yield self.factory_reset
        yield Label(f'{" DCT ":-^{SIDEBAR_WIDTH}}')
        self.dct = Label('', id=f'dct-label-{self.case.ref}')
        yield self.dct
        yield Label(f'{" DCT Exceptions ":-^{SIDEBAR_WIDTH}}')
        self.dct_exp = Label('', id=f'dct-exp-label-{self.case.ref}')
        yield self.dct_exp
        self.notes_sep = Label('')
        yield self.notes_sep
        self.notes = Label('', id=f'notes-label-{self.case.ref}')
        yield self.notes

        with VerticalGroup(id='lower-sidebar'):
            yield Label('TODO:')
            yield self.todo
            yield Label('')

            self.serial_label = Label(' '*(SIDEBAR_WIDTH-COPY_SERIAL_BUTTON_WIDTH), id=f'serial-label-{self.case.ref}')
            self.id_button = Button(f'Copy', id='copy-serial-button')
            self.id_button.can_focus = False
            with HorizontalGroup():
                yield self.serial_label
                yield self.id_button

            yield Label('')
            button = Button('Copy Notes', id='copy-button')
            button.can_focus = False
            yield button

    def on_button_pressed(self, event):
        match event.button.id:
            case 'copy-button':
                copy(self.case.text_area.text.strip())
            case 'copy-serial-button':
                copy(self.serial)
