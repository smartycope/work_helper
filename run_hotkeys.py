from hotkeys import *

keyboard.add_hotkey('ctrl+alt+k', order_part)
keyboard.add_hotkey('caps lock+alt+k', order_part)

keyboard.add_hotkey('ctrl+shift+alt+k', order_swap)
keyboard.add_hotkey('caps lock+shift+alt+k', order_swap)

keyboard.add_hotkey('ctrl+alt+l', add_repair_report)
keyboard.add_hotkey('caps lock+alt+l', add_repair_report)

keyboard.add_hotkey('alt+b', open_board)

keyboard.wait()
