from GraphController import States, DynamicStateMachine

class Steps(States):
    """ NOTE: within each phase these all need to be unique """

    manual_get_serial = "Enter the model number, or scan a serial number"
    todo = "TODO"
    _debug_mode = "You have entered debug mode. Enter the step or phase you would like to go to"

    # CONFRIM
    pick_up_case = "Go pick up the case on CSS {case ID} [done]"
    confirm_id = "Confirm IDs"
    ask_labels = "Put labels on everything [done]"
    turn_down_screwdriver = 'Turn down the power setting on the screwdriver [done]'
    check_repeat = "Is the case a repeat [no]"
    check_claimed_damage = "Check the claimed damage"
    ask_dock = "Additional dock, and any other parts (comma seperated) [no dock]"
    ask_damage = "Additional damage [no damage]"
    ask_came_with_bag = "Is there a bag in the dock [yes]"
    ask_came_with_pad = "Is there a pad on the bot [yes]"
    customer_states = "Customer States"
    update_css_failure = "Update the CSS failure box [done]"

    # ROUTINE_CHECKS
    # ask_modular = "Is the bot modular [yes]"
    check_liquid_damage = "Signs of liquid damage [no]"
    ask_sunken_contacts = "Do the contacts feel sunken (R/L/B) [no]"
    ask_blower_play = "Play in blower motor, or doesn't spin freely [no]"
    ask_rollers = "How do the extractors look [fine]"
    ask_s9_lid_pins = "Are the lid pins sunken [no]"
    ask_cleaned = 'Robot cleaned ["na" if not, notes or empty if so]'
    battery_test = "Battery test (don't forget the traveler) [current, <health>]"
    ask_user_base_contacts = "How do the charging contacts on the customer base look [fine]"
    ask_charge_customer_dock = "What's the charging wattage on the customer's dock [wattage or notes]"
    ask_charge_test_dock = "What's the charging wattage on a test base [wattage or notes]"
    ask_bin_rust = "Amount of rust on the tank screw [empty: none, 1: a spot, 2: entirely]"
    ask_dock_tank_rust ="Amount of rust on the dock's tank screw [empty: none, 1: a spot, 2: entirely]"
    ask_quiet_audio = 'Is the audio quiet or silent? (1: quiet, 2: silent) [no]'
    liquid_check_corrosion = "Is there corrosion on the board or connections (specify or empty for no)"
    liquid_check_dock = "Is there liquid residue in the customer dock [no]"
    liquid_check_bin = "Is there liquid residue in the robot bin [no]"
    liquid_check_voltage = "What's the voltage on the cx dock (it should be {s}) [swapping dock]"
    liquid_take_pictures = "Take pictures of liquid residue"

    # sunken_ask_measurement = "Contact measurement"
    sunken_ask_right_measurement = "Right contact measurement"
    sunken_ask_left_measurement = "Left contact measurement"

    # DEBUGGING
    add_step = "Add Step"

    # SWAP
    swap_unuse_parts = "Unuse all parts and get out of the case [done]"
    swap_update_css = "Update CSS repair action and copy notes over {{notes}} [done]"
    swap_email = "Send swap email {{address, subject, notes}} [confirmed]"
    swap_order_dock = 'Order a new dock [done] ("out" if out of stock)'
    swap_order = 'Reload case and order swap {{original serial}} ("out" if out of stock)'
    swap_order_S9 = 'Order a new chassis (not a whole bot!) {{original serial}} ("out" if out of stock) [done]'
    swap_order_M6 = 'Order the correctly colored swap ({s}) {{original serial}} ("out" if out of stock) [done]'
    swap_move_bin = 'Unbox and move bin and battery over ("fb", "new", "cx", or empty) [no bin needed]'
    # swap_put_in_box = "Put the old bot in the box [done]"
    swap_add_labels = 'Put labels on the new bot [done]'
    swap_ask_refurb = "Is the swapped bot a refurb? [yes]"
    swap_input_new_serial = "What's the serial number of the new bot"
    swap_note_serial = "Put the new serial number into CSS {{new serial}} [done]"

    # HOLD
    # hold_put_todo_in_notes = "Put any context directly into the notes {{TODO}} [done]"
    hold_copy_notes_to_CSS = "Copy notes over to CSS {{notes}} [done] " # The extra space here is important!
    hold_add_context = "Add any context about the case [done]"
    hold_unuse_parts = "Unuse any parts, but don't close out parts! [done]"
    hold_put_on_shelf = "Put everything together, and put on the shelf with the traveler [done]"
    hold_done = "Good to close case now! [close case]"

    # FINISH
    ask_bit_mobility_done = "Pass mobility and attempted BiT [done]"
    ask_lapis_mobility_done = "Pass mobility with a Lapis bin [done]"
    ask_m6_dry_mobility = "Pass mobility with a dry pad [done]"
    ask_removed_provisioning = "Remove provisioning [done]"
    # generate_external_notes = "Move notes over and add external notes and a repair action {{notes}} [done]"
    generate_external_notes = "Fill in CSS {s}{{notes}} [done]"
    # ask_copy_notes_1 = "Copy notes over to CSS and add a repair action {{notes}} [done]"
    ask_final_cleaned = "Cleaned the robot [done]"
    ask_base_cleaned = "Cleaned the base and cord tied up [done]"
    ask_dock_has_bag = "Does the dock have a bag [done]"
    ask_emptied_dock = "Dock tank is emptied [done]"
    ask_emptied_bin = "Bin is cleaned out and the debug cover is in place [done]"
    ask_emptied_tank = "Tank is emptied [done]"
    # ask_swap_serial = 'The swap serial number for new bot is entered [done]'
    ask_sidebrush_screws = "The bot has a sidebrush on and screws are tight [done]"
    ask_has_pad = "There's a clean pad on the bot [done]"
    ask_does_not_have_pad = "The pad is not on the bot [done]"
    # ask_tight_screws = "All screws are screwed in all the way [done]"
    # ask_debug_cover = "The debug cover is in place [done]"
    ask_double_check = "Have the case double checked {{address, subject, notes}} [sent]"
    double_check_confirmed = 'Wait for the case to be double checked [looks good]'
    ask_shipping_mode = "Placed into shipping mode [done]"
    ask_close_parts = "Close out all parts and get out of case [done]"
    ask_tags_off = "All tags are off and grab the traveler {s}[done]"
    ask_put_bin_back = "Put the bin back [done]"
    ask_copy_notes_2 = "Copy notes over to CSS {{notes}} [done]" # no extra space here!
    ask_submit_adj = "Send adjustment {{address, subject, adjustment}}"
    wait_parts_closed = 'Wait for parts to get closed out {{case ID}} [done]'
    ask_complete_case_CSS = "Finish the case on CSS {{case ID}} [done]"
    ask_put_bot_on_shelf = "Put the robot and traveler{s} on the shelf [done]"
    penultimate_step = 'Wait for parts, finish on CSS, then put on shelf {{case ID}} [done]'
    ask_put_bot_on_shelf_mopping = "Put the robot and traveler{s} on the shelf, and put the tank[s] on top [done]"
    finish_case = 'All done! [close case]'

    charging = 'Bot is charging [done]'
    updating = 'Bot is updating firmware [done]'

S = Steps

class StepsController(DynamicStateMachine):
    def __init__(self, case=None):
        super().__init__(
            Steps,
            Steps.pick_up_case,
            transitions = (
                S.pick_up_case          >> S.confirm_id,
                S.confirm_id            >> self.confirm_ids,
                S.turn_down_screwdriver >> S.ask_labels,
                S.ask_labels            >> S.check_repeat,
                S.check_repeat          >> S.check_claimed_damage,
                S.check_claimed_damage  >> S.ask_dock,
                S.ask_dock              >> S.ask_damage,
                S.ask_damage            >> self.ask_bag,
                S.ask_came_with_bag     >> self.ask_pad,
                S.ask_came_with_pad     >> S.customer_states,
                S.customer_states       >> S.update_css_failure,
            )
        )
        self.case = case

    def confirm_ids(self, resp):
        if resp:
            return S.confirm_id
        else:
            return self.screwdriver__labels

    def screwdriver__labels(self, resp):
        # return S.ask_labels if case.serial.startswith('m6') else S.turn_down_screwdriver
        if self.case.serial.startswith('m6'):
            return S.ask_labels
        else:
            return S.turn_down_screwdriver

    def ask_bag(self, resp):
        if self.case.is_dock:
            return S.ask_came_with_bag, 'if theres a dock'
        else:
            return self.ask_pad, 'if no dock'

    def ask_pad(self, resp):
        if self.case.is_combo:
            return S.ask_came_with_pad, 'if combo'
        else:
            return S.customer_states, 'otherwise'
