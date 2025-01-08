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
    ask_mobility = 'Mobility test [done]'
    ask_DCT = 'DCT [done]'
    ask_BBK = 'BBK [done]'
    ask_BBK = 'Battery test [done]'
    ask_emptied_tank = 'Have you emptied the tank [done]'
    ask_emptied_dock = 'Have you emptied the dock [done]'
    ask_dock_has_bag = 'Does the dock have a bag [done]'
    ask_put_bin_back = 'Have you put the bin back [done]'
    ask_final_cleaned = 'Cleaned the robot [done]'
    ask_base_cleaned = 'Cleaned the base [done]'
    ask_shipping_mode = 'Placed into shipping mode [done]'
    ask_complete_case_CSS = 'Finish the case on CSS [done]'
    # double check
    # all done (then closes case)
    # close out all parts and get out of case
    # swap serial number for new bot is entered
    # sidebrush is on
