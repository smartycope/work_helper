from textual import on
from textual.containers import *
from textual.widgets import *

from CustomInput import CustomInput
from Menu import Menu
from TriSwitch import TriSwitch

class MobilityMenu(Menu):
    switches = (
            'undock',
            'dock',
            'navigate',
            'picks_up_debris',
            'refill',
            'auto_evac',
            'manual_evac',
            'deploy_pad',
            'spray',
        )

    def __init__(self, case):
        # super().__init__(classes='mobility-menu', id=f'mobility-menu-{case.ref}')
        super().__init__(case)
        self._been_opened = False

    def compose(self):
        yield Label('[bold]Mobility Test[/]', id='mobility-title')

        self.cx_dock = Label('', id='cx-dock-label')
        yield self.cx_dock

        self.cx_states = Label('', id='cx-states')
        yield self.cx_states

        yield Label('Where:')
        self.where = Select.from_values(('top bench', 'floor', 'bottom bench'), allow_blank=False, value='floor')
        yield self.where

        # yield Label('Dock:')
        # self.base = CustomInput(('cx ' + self.case.dock) if self.case.dock else 'test ', placeholder='no dock', id='dock-input')
        # yield self.base
        self.base1 = Select(((i, i) for i in ('cx', 'test', 'new', '#2', '#3')), allow_blank=False)
        self.base2 = Select([], prompt='No Dock')
        yield self.base1
        yield self.base2

        yield Label('Parameters:')
        self.params = CustomInput(classes='triple', placeholder='Additional parameters')
        yield self.params

        yield Rule(line_style='heavy', classes='quadruple')

        self.undock_label = Label('Undock:')
        yield self.undock_label
        self.undock = TriSwitch(value=True)
        yield self.undock

        self.picks_up_debris_label = Label('Picks up Debris:')
        yield self.picks_up_debris_label
        self.picks_up_debris = TriSwitch(value=None)
        yield self.picks_up_debris

        self.navigate_label = Label('Navigate:')
        yield self.navigate_label
        self.navigate = TriSwitch(value=True)
        yield self.navigate

        self.refill_label = Label('Refill:')
        yield self.refill_label
        self.refill = TriSwitch(value=None, disabled=self.case.is_combo is False)
        yield self.refill

        self.dock_label = Label('Dock:')
        yield self.dock_label
        self.dock = TriSwitch(value=True)
        yield self.dock

        self.deploy_pad_label = Label('Deploy Pad:')
        yield self.deploy_pad_label
        self.deploy_pad = TriSwitch(value=None, disabled=self.case.is_combo is False)
        yield self.deploy_pad

        self.auto_evac_label = Label('Auto Evac:')
        yield self.auto_evac_label
        self.auto_evac = TriSwitch(value=None)
        yield self.auto_evac

        self.num_lines_label = Label('Num Lines:')
        yield self.num_lines_label
        self.num_lines = MaskedInput(template="9", id='num-lines', disabled=self.case.is_combo is False)
        yield self.num_lines

        self.manual_evac_label = Label('Manual Evac:')
        yield self.manual_evac_label
        self.manual_evac = TriSwitch(value=None)
        yield self.manual_evac

        self.spray_label = Label('Spray:')
        yield self.spray_label
        self.spray = TriSwitch(value=None)
        yield self.spray

        # yield Static(classes='double')
        yield Static(classes='quadruple')

        # yield Label('Notes')
        self.notes = CustomInput(placeholder='Notes', classes='quadruple', id='notes')
        yield self.notes

        # yield Static(classes='quadruple')
        # yield Static(classes='double')
        self.todo = Input(placeholder='Temporary Notes', classes='double extend')
        yield self.todo

        yield Button('Close', id='cancel', classes='mm-buttons', action='close')
        yield Button('Done', id='done', classes='mm-buttons')

    def reset(self):
        """ Run whenever the menu gets closed """
        self.notes.value = ''
        self.todo.value = ''

    def setup(self):
        """ Run at the very beginning, but after everything is mounted """
        self.reset()
        self.cx_states.update(('| cx: ' + self.case.customer_states) if self.case.customer_states else '')
        self.cx_dock.update('| dock: ' + self.case.dock if self.case.dock else 'No dock')
        self.base1.value = 'cx' if self.case.dock else 'test'
        self.base2.set_options((i, i) for i in self.case.get_docks())
        self.base2.value = (
            self.case.dock
            if self.case.dock in self.case.get_docks()
            else self.case.get_docks()[0]
        )
        # Disable the non-relevant tests
        disabled_text = '#666666'
        if self.case.serial.startswith('m6'):
            self.auto_evac.disabled = True
            self.auto_evac_label.styles.color = disabled_text
            self.manual_evac.disabled = True
            self.manual_evac_label.styles.color = disabled_text
            self.picks_up_debris.disabled = True
            self.picks_up_debris_label.styles.color = disabled_text
            self.refill.disabled = True
            self.refill_label.styles.color = disabled_text
            self.deploy_pad.disabled = True
            self.deploy_pad_label.styles.color = disabled_text
            self.num_lines.disabled = True
            self.num_lines_label.styles.color = disabled_text
        elif not self.case.can_mop:
            self.refill.disabled = True
            self.refill_label.styles.color = disabled_text
            self.deploy_pad.disabled = True
            self.deploy_pad_label.styles.color = disabled_text
            self.num_lines.disabled = True
            self.num_lines_label.styles.color = disabled_text
            self.spray.disabled = True
            self.spray_label.styles.color = disabled_text
        else:
            self.spray.disabled = True
            self.spray_label.styles.color = disabled_text

    def action_toggle(self):
        super().action_toggle()
        # The first time, we need to update everything. After that, update only after we insert one
        if not self._been_opened:
            self._been_opened = True
            self.setup()

    def action_close(self):
        self.case.text_area.scroll_to(None, 1000, animate=False)
        self.case.input.focus()
        return super().action_close()

    @on(Input.Submitted, '#dock-input')
    @on(Input.Submitted, '#notes')
    @on(Button.Pressed, '#done')
    def done(self):
        extra_line = '' if self.case.text_area.text.strip().endswith('Process:') else '\n'
        self.case.text_area.text = self.case.text_area.text.strip() + '\n' + extra_line + self.stringify() + '\n\n'
        self.reset()
        # self.case.input.focus()
        self.action_close()

    def stringify(self):
        has_pass = any(getattr(self, i).value for i in self.switches)
        has_fail = any(getattr(self, i).value is False for i in self.switches)

        lines_pass = None
        if self.num_lines.value:
            try:
                lines = int(self.num_lines.value)
                lines_pass = lines >= 2
            except:
                lines_pass = None

        # ...we didn't test anything?
        if not has_pass and not has_fail and lines_pass is None:
            return

        l1 = "* Mobility test - {where}, {base}".format(
            where=self.where.value,
            base=(self.base1.value + ' ' + self.base2.value if type(self.base2.value) is str else 'no dock'),
        )
        if self.params.value:
            l1 += ', ' + self.params.value

        l2 = "** "
        if has_pass or lines_pass is True:
            l2 += 'Pass: ' + ', '.join(
                i.replace('_', ' ')
                for i in self.switches
                if getattr(self, i).value # and i != 'other_value'
            )

        if lines_pass:
            if has_pass:
                l2 += ', '
            l2 += f'{self.num_lines.value} lines'

        if has_fail or lines_pass is False:
            if has_pass or lines_pass is True:
                l2 += ' | '
            l2 += 'Fail: ' + ', '.join(
                i.replace('_', ' ')
                for i in self.switches
                if getattr(self, i).value is False # and i != 'other_value'
            )

        if lines_pass is False:
            if has_fail:
                l2 += ', '
            l2 += f'{self.num_lines.value} lines'

        l3 = '** Result: ' + ("Fail" if has_fail or lines_pass is False else 'Pass')
        if self.notes.value:
            l3 += ' - ' + self.notes.value

        return '\n'.join((l1, l2, l3))
