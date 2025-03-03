from hotkeys import *

keyboard.add_hotkey('ctrl+alt+k', order_part)
keyboard.add_hotkey('caps lock+alt+k', order_part)

keyboard.add_hotkey('ctrl+shift+alt+k', order_swap)
keyboard.add_hotkey('caps lock+shift+alt+k', order_swap)

keyboard.add_hotkey('ctrl+alt+l', add_repair_report)
keyboard.add_hotkey('caps lock+alt+l', add_repair_report)

keyboard.add_hotkey('alt+b', open_board)
keyboard.add_hotkey('alt+p', query_case)
keyboard.add_hotkey('alt+r', open_return_product)
keyboard.add_hotkey('alt+q', open_ship_product)
keyboard.add_hotkey('alt+i', search_for_swap)
keyboard.add_hotkey('alt+x', search_for_swap)
keyboard.add_hotkey('alt+v', add_case)

keyboard.wait()
