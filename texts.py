class Steps:
    manual_get_serial = 'Enter the model number, or scan a serial number'
    todo = 'TODO'

    confirm_id = 'Confirm IDs'
    check_repeat = 'Check if case is a repeat'
    check_spl_sku = 'Check that the SPL SKU is valid'
    pick_up_case = 'Go pick up the case on CSS (case ID copied)'
    ask_dock = 'Additional dock'
    ask_damage = 'Additional damage'
    customer_states = 'Customer States'
    check_liquid_damage = 'Signs of liquid damage [no]'
    ask_sunken_contacts = 'Sunken contacts [no]'
    ask_blower_play = 'Play in blower motor, or doesn\'t spin freely [no]'
    ask_rollers = 'Extractors are good [yes]'
    ask_s9_lid_pins = 'Are the lid pins sunken [no]'
    ask_cleaned = 'Robot cleaned ("na" if not, notes or empty if so)'
    battery_test = 'Battery test (don\'t forget the traveller) [current, health]'
    ask_user_base_contacts = 'Are the charging contacts on the user base good [yes]'
    ask_charge_customer_dock = "What's the charging wattage on the customer's dock"
    ask_charge_test_dock = "What's the charging wattage on a test base"
    ask_bin_rust = "Amount of rust on the tank screw [empty: none, 1: a spot, 2: entirely]"

    liquid_check_corrosion = 'Is there corrosion on the board or connections (specify or empty for no)'
    liquid_check_dock = 'Is there liquid residue in the user dock [no]'
    liquid_check_bin = 'Is there liquid residue in the robot bin [no]'
    liquid_take_pictures = 'Take pictures of liquid residue'

    sunken_ask_side = 'Which side is sunken (R/L)'
    sunken_ask_measurement = 'Contact measurement'

    add_step = 'Add Step'

    # TODO:
    # ask_mobility = 'Mobility test [done]'
    # ask_DCT = 'DCT [done]'
    # ask_BBK = 'BBK [done]'
    # ask_BBK = 'Battery test [done]'
    ask_final_cleaned = 'Cleaned the robot [done]'
    ask_base_cleaned = 'Cleaned the base [done]'
    ask_dock_has_bag = 'Does the dock have a bag [done]'
    ask_emptied_dock = 'Dock tank is emptied [done]'
    ask_emptied_bin = 'Bin is cleaned out [done]'
    ask_emptied_tank = 'Tank is emptied [done]'
    # ask_swap_serial = 'The swap serial number for new bot is entered [done]'
    ask_sidebrush = 'The bot has a sidebrush on [done]'
    ask_has_pad = "There's a pad on the bot [done]"
    ask_tight_screws = "All screws are screwed in all the way [done]"
    ask_debug_cover = 'The debug cover is in place [done]'
    ask_double_check = "Have the case double checkd [good]"
    ask_shipping_mode = 'Placed into shipping mode [done]'
    ask_close_parts = 'Close out all parts and get out of case [done]'
    ask_tags_off = "All the tags are off, including the bin and dock [done]"
    ask_put_bin_back = 'Put the bin back [done]'
    ask_complete_case_CSS = 'Finish the case on CSS [done]'
    ask_put_bot_on_shelf = 'Put the robot on the shelf [done]'
    # finish_case = 'All done! [close case]'
    finish_case = 'All done! Good to close case now'
