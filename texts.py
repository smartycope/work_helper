# NOTE: these all need to be unique (though it's not enforced)
from numpy import double


class Steps:
    manual_get_serial = "Enter the model number, or scan a serial number"
    todo = "TODO"

    # CONFRIM
    ask_labels = "Put labels on everything"
    confirm_id = "Confirm IDs"
    check_repeat = "Check if case is a repeat"
    check_spl_sku = "Check that the SPL SKU is valid"
    pick_up_case = "Go pick up the case on CSS {case ID} [done]"
    ask_dock = "Additional dock"
    ask_damage = "Additional damage"
    ask_came_with_bag = "Is there a bag in the dock [yes]"
    customer_states = "Customer States"
    update_css_failure = "Update the CSS failure box [done]"

    # ROUTINE_CHECKS
    ask_modular = "Is the bot modular [yes]"
    check_liquid_damage = "Signs of liquid damage [no]"
    ask_sunken_contacts = "Do the contacts feel sunken [no]"
    ask_blower_play = "Play in blower motor, or doesn't spin freely [no]"
    ask_rollers = "How do the extractors look [good]"
    ask_s9_lid_pins = "Are the lid pins sunken [no]"
    ask_cleaned = 'Robot cleaned ("na" if not, notes or empty if so)'
    battery_test = "Battery test (don't forget the traveller) [current, health]"
    ask_user_base_contacts = "How do the charging contacts on the user base look [good]"
    ask_charge_customer_dock = "What's the charging wattage on the customer's dock"
    ask_charge_test_dock = "What's the charging wattage on a test base"
    ask_bin_rust = "Amount of rust on the tank screw [empty: none, 1: a spot, 2: entirely]"
    ask_dock_tank_rust ="Amount of rust on the dock's tank screw [empty: none, 1: a spot, 2: entirely]"
    liquid_check_corrosion = "Is there corrosion on the board or connections (specify or empty for no)"
    liquid_check_dock = "Is there liquid residue in the user dock [no]"
    liquid_check_bin = "Is there liquid residue in the robot bin [no]"
    liquid_take_pictures = "Take pictures of liquid residue"

    sunken_ask_side = "Which side is sunken (R/L/B)"
    # sunken_ask_measurement = "Contact measurement"
    sunken_ask_right_measurement = "Right contact measurement"
    sunken_ask_left_measurement = "Left contact measurement"

    # DEBUGGING
    add_step = "Add Step"

    # SWAP
    swap_unuse_parts = "Unuse all parts and get out of the case[done]"
    swap_update_css = "Update CSS repair action and copy notes over {notes} [done]"
    swap_email = "Send swap email {address, subject, notes} [confirmed]"
    swap_order = "Order swap {original serial} [done]"
    swap_order_S9 = "Order main board (not a whole bot!) [done]"
    swap_order_M6 = "Order the correctly colored swap [done]"
    swap_move_bin = "Move bin and battery over, if necessary [no bin needed]"
    swap_put_in_box = "Put the old bot in the box [done]"
    swap_note_serial = "Put the new (and old) serial number into CSS [done]"

    # FINISH
    ask_final_cleaned = "Cleaned the robot [done]"
    ask_base_cleaned = "Cleaned the base [done]"
    ask_dock_has_bag = "Does the dock have a bag [done]"
    ask_emptied_dock = "Dock tank is emptied [done]"
    ask_emptied_bin = "Bin is cleaned out [done]"
    ask_emptied_tank = "Tank is emptied [done]"
    # ask_swap_serial = 'The swap serial number for new bot is entered [done]'
    ask_sidebrush_screws = "The bot has a sidebrush on and screws are tight [done]"
    ask_has_pad = "There's a clean pad on the bot [done]"
    ask_does_not_have_pad = "The pad is not on the bot [done]"
    # ask_tight_screws = "All screws are screwed in all the way [done]"
    ask_debug_cover = "The debug cover is in place [done]"
    ask_double_check = "Have the case double checked {address, subject, notes} [sent]"
    double_check_confirmed = 'Wait for the case to be double checked [looks good]'
    ask_shipping_mode = "Placed into shipping mode [done]"
    ask_close_parts = "Close out all parts and get out of case [done]"
    ask_tags_off = "All the tags are off, including the bin and dock [done]"
    ask_put_bin_back = "Put the bin back [done]"
    ask_copy_notes_1 = "Copy notes over to CSS and add a repair action {notes} [done]"
    ask_copy_notes_2 = "Copy notes over to CSS {notes} [done]"
    ask_complete_case_CSS = "Finish the case on CSS {case ID, then 'rr'} [done]"
    ask_put_bot_on_shelf = "Put the robot and traveler on the shelf [done]"
    generate_external_notes = "Create and copy external notes [done]";
    # finish_case = 'All done! [close case]'
    finish_case = "All done! Good to close case now"
