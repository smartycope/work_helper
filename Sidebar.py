from clipboard import copy
from textual.containers import *
from textual.widgets import *
from info import sleep_mode, factory_reset
from Phase import Phase
from globals import COLORS, SIDEBAR_WIDTH, COPY_SERIAL_BUTTON_WIDTH
from CopyText import CopyText

class TodoTextArea(TextArea):
    BINDINGS = (
        Binding('ctrl+a', 'select_all', 'Select All', show=False),
    )

    def __init__(self, *a, **kw):
        super().__init__(*a, id='todo-textarea', **kw)
        self.cursor_blink = False


class Sidebar(VerticalGroup):
    def __init__(self, case):
        # super().__init__(id='sidebar-' + str(case.color))
        self.has_mounted = False
        super().__init__(classes='sidebar', id='sidebar-' + case.ref)
        self.case = case
        self.styles.background = self.case.color
        self.todo = TodoTextArea()
        self.phase_selector = Select([(i.name, i.value) for i in Phase], id='phase-select', allow_blank=False)
        self.phase_selector.can_focus = False

        # self.ref_model = Label(f'{self.case.ref:^{SIDEBAR_WIDTH}}\n', id=f'ref-label-{self.case.ref}')
        # self.ref_model = Label(f'{self.case.ref:^{SIDEBAR_WIDTH}}\n', id=f'ref-label-{self.case.ref}')
        self.ref = CopyText(self.case.ref, id=f'ref-label-{self.case.ref}')
        self.model = Label("")
        self.color_switcher = Select(
            [(f'[{color}]{name}[/]', color) for color, name in COLORS.items()],
            id="color-selector",
            allow_blank=False,
            value=self.case.color,
        )
        self.color_switcher.can_focus = False
        self.sleep_mode = Label('', id=f'sleep-mode-label-{self.case.ref}', classes='sidebar-label')
        self.factory_reset = Label('', id=f'factory-reset-label-{self.case.ref}', classes='sidebar-label')
        self.dct = Label('', id=f'dct-label-{self.case.ref}', classes='sidebar-label')
        self.dct_exp = Label('', id=f'dct-exp-label-{self.case.ref}', classes='sidebar-label')
        self.notes_sep = Label('', classes='sidebar-label')
        self.notes = Label('', id=f'notes-label-{self.case.ref}', classes='sidebar-label')
        # self.serial_label = Label(' '*(SIDEBAR_WIDTH-COPY_SERIAL_BUTTON_WIDTH), id=f'serial-label-{self.case.ref}')
        self.serial_labels = []
            # CopyText(' '*(SIDEBAR_WIDTH), None, id=f'serial-label-{self.case.ref}', classes='serial-label')
        # ]
        self.lower_sidebar = VerticalGroup(id='lower-sidebar')
        self.serial_buttons = VerticalGroup(id='serial-buttons')
        self.original_serial_label = CopyText(' '*(SIDEBAR_WIDTH), None, id=f'serial-label-{self.case.ref}', classes='serial-label')
        self.num_swaps = 0
        # self.id_button = Button(f'Copy', id='copy-serial-button')
        # self.id_button.can_focus = False

    def update(self):
        if not self.case.serial or not self.has_mounted:
            return

        self.model.update(f' • {self.case.get_quick_model()}')
        self.sleep_mode.update(sleep_mode.get(self.serial[0], 'Unknown') + '\n')
        self.factory_reset.update(factory_reset.get(self.serial[0], 'Unknown') + '\n')
        self.dct.update(f'DCT: {self.case.get_DCT()}\n')
        self.dct_exp.update(f'{{:^{SIDEBAR_WIDTH}}}'.format(self.case.get_DCT_exceptions()) + '\n')
        self.original_serial_label.text = f'O: {self.case.serials[0].upper():^{SIDEBAR_WIDTH}}'
        # Helpful for debugging
        # self.dct.update(json.dumps(self.case.serials, indent=2))
        self.original_serial_label.to_copy = self.case.serials[0].upper()
        while self.num_swaps < len(self.case.serials) - 1:
            serial = self.case.serials[self.num_swaps+1]
            self.serial_buttons.mount(CopyText(f'S{self.num_swaps}: {serial.upper():^{SIDEBAR_WIDTH}}', serial.upper()))
            self.num_swaps += 1

        notes = self.case.get_notes()
        if notes:
            self.notes_sep.update(f'{" Notes ":-^{SIDEBAR_WIDTH}}')
            self.notes.update(notes)

    def compose(self):
        self.has_mounted = True

        yield self.color_switcher

        with HorizontalGroup(classes='align-center'):
            # Quick hack, cause CSS is stupid
            yield Label(' '*((SIDEBAR_WIDTH-7)//2))
            yield self.ref
            yield self.model

        with HorizontalGroup():
            yield Label("\nPhase: ")
            yield self.phase_selector

        with ScrollableContainer():
            yield Label('\n')
            yield self.dct
            yield Label(f'{" DCT Exceptions ":-^{SIDEBAR_WIDTH}}', classes='sidebar-label')
            yield self.dct_exp
            yield Label(f'{" Shipping Mode ":-^{SIDEBAR_WIDTH}}', classes='sidebar-label')
            yield self.sleep_mode
            yield Label(f'{" Factory Reset ":-^{SIDEBAR_WIDTH}}', classes='sidebar-label')
            yield self.factory_reset
            yield self.notes_sep
            yield self.notes

        # yield Static(id='spacer')

        with self.lower_sidebar:
            # yield Label('TODO:')
            yield self.todo

            with self.serial_buttons:
                yield self.original_serial_label

            button = Button('Copy Notes', id='copy-button')
            button.can_focus = False
            yield button

        try: self.update()
        except: pass

    def on_button_pressed(self, event):
        match event.button.id:
            case 'copy-button':
                copy(self.case.text_area.text.strip())
            case 'copy-serial-button':
                copy(self.serial.upper())

    @property
    def serial(self):
        return self.case.serial or ''
