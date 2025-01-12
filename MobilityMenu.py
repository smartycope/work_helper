from textual.containers import *
from textual.reactive import reactive
from textual.widgets import *

class TriSwitch(Switch):
    DEFAULT_CSS = """
    TriSwitch {
        border: tall $border-blurred;
        background: $surface;
        height: auto;
        width: auto;

        padding: 0 2;
        &.-on .switch--slider {
            color: $success;
        }
        &.-off .switch--slider {
            color: $error;
        }
        & .switch--slider {
            color: $panel;
            background: $panel-darken-2;
        }
        &:hover {
            & > .switch--slider {
                color: $panel-lighten-1
            }
            &.-on > .switch--slider {
                color: $success-lighten-1;
            }
            &.-off > .switch--slider {
                color: $error-lighten-1;
            }
        }
        &:focus {
            border: tall $border;
            background-tint: $foreground 5%;
        }

        &:light {
            &.-on .switch--slider {
                color: $success;
            }
            &.-off .switch--slider {
                color: $error;
            }
            & .switch--slider {
                color: $primary 15%;
                background: $panel-darken-2;
            }
            &:hover {
                & > .switch--slider {
                    color: $primary 25%;
                }
                &.-on > .switch--slider {
                    color: $success-lighten-1;
                }
                &.-off > .switch--slider {
                    color: $error-lighten-1;
                }
            }
        }
    }
    """

    def __init__(
        self,
        value: bool = False,
        *,
        animate: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        tooltip = None,
    ):
        super().__init__(name=name, id=id, classes=classes, disabled=disabled, animate=animate, tooltip=tooltip)
        if value is True:
            self._slider_position = 1.0
            self.set_reactive(Switch.value, value)
        elif value is None:
            self._slider_position = 0.5
            self.set_reactive(Switch.value, value)
        # self._should_animate = animate
        # if tooltip is not None:
        #     self.tooltip = tooltip

    def toggle(self):
        match self.value:
            case True:  self.value = False
            case False: self.value = None
            case None:  self.value = True
        return self

    def watch_value(self, value: bool|None) -> None:
        # target_slider_position = 1.0 if value else 0.0
        match self.value:
            case True:  target_slider_position = 1.0
            case False: target_slider_position = 0.0
            case None:  target_slider_position = 0.5

        if self._should_animate:
            self.animate(
                "_slider_position",
                target_slider_position,
                duration=0.3,
                level="basic",
            )
        else:
            self._slider_position = target_slider_position
        self.post_message(self.Changed(self, self.value))

    def watch__slider_position(self, slider_position: float) -> None:
        self.set_class(slider_position == 1, "-on")
        self.set_class(slider_position == 0, "-off")
        # self.style.
        # self.set_class(self.value is True, "-on")
        # self.set_class(self.value is None, "-off")


class MobilityMenu(VerticalGroup):
    def __init__(self, case):
        super().__init__(classes='mobility-menu', id=f'mobility-menu-{case.ref}')
        self.visible = False
        self.case = case

    # def watch_visible(self):


    def compose(self):
        yield Label('[bold]Mobility Test[/]', id='mobility-title')

        yield Label('Where:')
        self.where = Select.from_values(('top bench', 'floor', 'bottom bench'), allow_blank=False, value='top bench')
        yield self.where

        yield Label('Dock:')
        self.base = Input(('customer ' + self.case.dock) if self.case.dock else 'test ')
        yield self.base

        yield Label('Parameters:')
        self.params = Input(classes='triple', placeholder='Additional parameters')
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

        yield Label('Picks up Rice:')
        self.rice = TriSwitch(value=None)
        yield self.rice

        # yield Label('Streaky:')
        # self.streaky = TriSwitch(value=None)
        # yield self.streaky

        # self.other = Input(placeholder='Other:')
        # yield self.other
        # self.other_value = TriSwitch(value=None)
        # yield self.other_value

        yield Static(classes='double')
        yield Static(classes='quadruple')

        # yield Label('Notes')
        self.notes = Input(placeholder='Notes', classes='quadruple')
        yield self.notes

        yield Static(classes='quadruple')
        yield Static(classes='double')

        yield Button('Cancel', id='cancel', classes='')
        yield Button('Done', id='done', classes='')

    def on_button_pressed(self, event):
        match event.button.id:
            case 'cancel':
                self.visible = False
            case 'done':
                self.visible = False
                self.case.text_area.text = self.case.text_area.text.strip() + '\n\n' + self.stringify() + '\n\n'

    def stringify(self):
        switches = (
            'undock',
            'base',
            'navigate',
            'rice',
            'refill',
            'auto_evac',
            'manual_evac',
            'deploy_pad',
            # 'streaky',
            # 'other_value',
        )
        has_pass = any(getattr(self, i).value for i in switches)
        has_fail = any(getattr(self, i).value is False for i in switches)

        # ...we didn't test anything?
        if not has_pass and not has_fail:
            return

        l1 = "* Mobility test - {where}, {base}".format(
            where=self.where.value,
            base=self.base.value,
        )
        if self.params.value:
            l1 += ', ' + self.params.value

        l2 = "** "
        if has_pass:
            l2 += 'Pass: ' + ', '.join(
                i.replace('_', ' ')
                for i in switches
                if getattr(self, i).value # and i != 'other_value'
            )
        if has_fail:
            if has_pass:
                l2 += ' | '
            l2 += 'Fail: ' + ', '.join(
                i.replace('_', ' ')
                for i in switches
                if getattr(self, i).value is False # and i != 'other_value'
            )

        l3 = '** Result: ' + ("Fail" if has_fail else 'Pass')
        if self.notes.value:
            l3 += ' - ' + self.notes.value

        return '\n'.join((l1, l2, l3))
