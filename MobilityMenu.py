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
        self.cx_states = Label('Customer States: ', id='cx-states')
        yield self.cx_states

        yield Label('Where:')
        self.where = Select.from_values(('top bench', 'floor', 'bottom bench'), allow_blank=False, value='top bench')
        yield self.where

        yield Label('Dock:')
        self.base = CustomInput(('cx ' + self.case.dock) if self.case.dock else 'test ', placeholder='no dock')
        yield self.base

        yield Label('Parameters:')
        self.params = CustomInput(classes='triple', placeholder='Additional parameters')
        yield self.params

        yield Rule(line_style='heavy', classes='quadruple')

        yield Label('Undock:')
        self.undock = TriSwitch(value=True)
        yield self.undock

        yield Label('Num Lines:')
        self.num_lines = MaskedInput(template="9", id='num-lines', disabled=self.case.is_combo is False)
        yield self.num_lines

        yield Label('Refill:')
        self.refill = TriSwitch(value=None, disabled=self.case.is_combo is False)
        yield self.refill

        yield Label('Dock:')
        self.dock = TriSwitch(value=True)
        yield self.dock

        yield Label('Deploy Pad:')
        self.deploy_pad = TriSwitch(value=None, disabled=self.case.is_combo is False)
        yield self.deploy_pad

        yield Label('Auto Evac:')
        self.auto_evac = TriSwitch(value=None)
        yield self.auto_evac

        yield Label('Navigate:')
        self.navigate = TriSwitch(value=True)
        yield self.navigate

        yield Label('Manual Evac:')
        self.manual_evac = TriSwitch(value=None)
        yield self.manual_evac

        yield Label('Picks up Debris:')
        self.picks_up_debris = TriSwitch(value=None)
        yield self.picks_up_debris

        yield Label('Spray:')
        self.spray = TriSwitch(value=None)
        yield self.spray

        # yield Static(classes='double')
        yield Static(classes='quadruple')

        # yield Label('Notes')
        self.notes = CustomInput(placeholder='Notes', classes='quadruple')
        yield self.notes

        # yield Static(classes='quadruple')
        # yield Static(classes='double')
        self.todo = TextArea(classes='double extend')
        yield self.todo

        yield Button('Close', id='cancel', classes='')
        yield Button('Done', id='done', classes='')

    def update_values(self):
        """ Run whenever the menu gets closed """
        # If we have a dock, always assume we're using it
        if self.case.dock and (not self.base.value or self.base.value == 'test '):
            self.base.value = 'cx ' + self.case.dock
        self.notes.value = ''
        self.todo.text = ''

    def action_toggle(self):
        super().action_toggle()
        # The first time, we need to update everything. After that, update only after we insert one
        if not self._been_opened:
            self.update_values()
            self._been_opened = True
            self.cx_states.update('| cx: ' + self.case.customer_states if self.case.customer_states else '')

    def on_button_pressed(self, event):
        match event.button.id:
            case 'cancel':
                self.visible = False
            case 'done':
                self.visible = False
                extra_line = '' if self.case.text_area.text.strip().endswith('Process:') else '\n'
                self.case.text_area.text = self.case.text_area.text.strip() + '\n' + extra_line + self.stringify() + '\n\n'
                self.update_values()

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
            base=self.base.value or 'no dock',
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
