from textual.containers import *
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
