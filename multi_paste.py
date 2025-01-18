import keyboard, clipboard, os
from time import monotonic


__PASTE_SCHEDULE = []
# A dict of {multi_paste call id: hotkey instances}
# The reason we keep track of this is so it can delete itself from _increment_paste() after the
# pastes are all consumed, for housekeeping purposes
__HOTKEY_HOOKS = {}

def _increment_paste(id):
    global __HOTKEY_HOOKS, __PASTE_SCHEDULE
    print(__PASTE_SCHEDULE)
    if __PASTE_SCHEDULE:
        clipboard.copy(__PASTE_SCHEDULE.pop(0))
    # Not an else here, cause the size may have changed now
    if not __PASTE_SCHEDULE:
        for i in __HOTKEY_HOOKS.pop(id):
            keyboard.remove_hotkey(i)

def _clear_schedule():
    global __PASTE_SCHEDULE
    __PASTE_SCHEDULE = []
    # I don't need to remove everything right now, cause _increment_paste() will handle that for me

if os.name == 'nt':
    def multi_paste(*pastes, clear=True, caps_lock=True):
        """ Paste multiple things in order. Each time you paste something, it'll switch to the next thing.
            The first element will be set as the clipboard immediately, and the last element will be the
            text left on the keyboard after all the pastes are consumed.
            If caps_lock is True, it assumes caps lock acts like a control.
            This function will not block execution, and stops functioning after execution is halted.
            If clear, then using this function will override any previous uses of it. For example, if you
            call this function with 5 arguments, and only paste twice, then call this function again, it
            will clear the other 3 pastes. If clear is set to False, then they will be appended to the
            scheduled pastes.
        """
        global __HOTKEY_HOOKS, __PASTE_SCHEDULE

        if clear:
            __PASTE_SCHEDULE = list(pastes)
        else:
            __PASTE_SCHEDULE += list(pastes)

        # Just a unique id so we can share the values returned by add_hotkey with _increment_paste(), so
        # we can delete from there
        id = monotonic()

        params = dict(callback=_increment_paste, args=(id,), suppress=False, trigger_on_release=False)
        try:
            __HOTKEY_HOOKS[id] = (
                keyboard.add_hotkey('ctrl+v', **params),
                keyboard.add_hotkey('caps lock+v', **params)
            )
            keyboard.add_hotkey('ctrl+c', _clear_schedule)
            keyboard.add_hotkey('caps lock+c', _clear_schedule)
            # _increment_paste(id)
            clipboard.copy(pastes[0])
        except ImportError:
            clipboard.copy(pastes[-1])
else:
    def multi_paste(*pastes, clear=True, caps_lock=True):
        """ Paste multiple things in order. Each time you paste something, it'll switch to the next thing.
            The first element will be set as the clipboard immediately, and the last element will be the
            text left on the keyboard after all the pastes are consumed.
            If caps_lock is True, it assumes caps lock acts like a control.
            This function will not block execution, and stops functioning after execution is halted.
            If clear, then using this function will override any previous uses of it. For example, if you
            call this function with 5 arguments, and only paste twice, then call this function again, it
            will clear the other 3 pastes. If clear is set to False, then they will be appended to the
            scheduled pastes.
        """
        global __HOTKEY_HOOKS, __PASTE_SCHEDULE

        if clear:
            __PASTE_SCHEDULE = list(pastes)
        else:
            __PASTE_SCHEDULE += list(pastes)

        # Just a unique id so we can share the values returned by add_hotkey with _increment_paste(), so
        # we can delete from there
        id = monotonic()

        params = dict(callback=_increment_paste, args=(id,), suppress=True, trigger_on_release=True)
        try:
            __HOTKEY_HOOKS[id] = (
                keyboard.add_hotkey('ctrl+v', **params),
                keyboard.add_hotkey('caps lock+v', **params)
            )
            keyboard.add_hotkey('ctrl+c', _clear_schedule)
            keyboard.add_hotkey('caps lock+c', _clear_schedule)
            _increment_paste(id)
        except ImportError:
            clipboard.copy(pastes[-1])


# For manual testing
if __name__ == '__main__':
    # clipboard.copy('test')
    multi_paste('a', 'b', 'c', 'd')
    keyboard.wait()
