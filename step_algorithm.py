from clipboard import copy
from textual.containers import *
from textual.widgets import *
from Phase import Phase
from texts import Steps


def execute_step(self, resp):
    # To simplify some of the redundant next step logic
    next_step = None

    # TODO: I think back isn't working
    if resp.lower() == 'back' and self.step != Steps.confirm_id:
        self.step = self.prev_step
        return

    if self.step == Steps.manual_get_serial:
        if resp:
            self.serial = resp.lower()
            self.sidebar.serial = self.serial.lower()
            self.step = self._step_after_manual_serial
        return

    if self.phase == Phase.CONFIRM:
        match self.step:
            # Main path
            case Steps.ask_labels:
                self.step = Steps.confirm_id

            case Steps.confirm_id:
                # If we (somehow) already have the serial number, we don't need to confirm it
                if self.serial:
                    self.step = Steps.check_repeat
                    return

                ids=  resp.lower()
                if not resp:
                    # If they don't put anything, assume we aren't comparing serial numbers, and we just want to input one
                    self.ensure_serial(Steps.check_repeat)
                    return
                else:
                    if len(ids) % 2:
                        self.text_area.text = self.step = '!!! Serial numbers are different lengths !!!'
                        return
                    else:
                        half = len(ids)//2
                        if ids[half:] != ids[:half]:
                            self.text_area.text = self.step = '!!! Serial numbers are different !!!'
                            return
                    self.serial = ids[len(resp)//2:].lower()
                    # Fill in all the info now that we have the serial number
                    self.sidebar.serial = self.serial
                    self.step = Steps.check_repeat

            case Steps.check_repeat:
                self.step = Steps.check_spl_sku

            case Steps.check_spl_sku:
                copy(self.ref)
                self.step = Steps.pick_up_case

            case Steps.pick_up_case:
                self.step = Steps.ask_dock

            case Steps.ask_dock:
                self.dock = resp
                self.text_area.text += 'Parts in: Robot'
                if resp:
                    self.text_area.text += ', ' + resp + ', cord'
                self.text_area.text += '\n'
                self.step = Steps.ask_damage

            case Steps.ask_damage:
                self.text_area.text += 'Claimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage'
                if resp:
                    self.text_area.text += ', ' + resp[0].lower() + resp[1:]
                self.text_area.text += '\n'
                self.step = Steps.customer_states

            case Steps.customer_states:
                if resp:
                    self.customer_states = resp[0].upper() + resp[1:]
                    self.text_area.text += 'Customer States: ' + self.customer_states + '\n\nRoutine Checks:\n'
                    self.step = Steps.update_css_failure

            case Steps.update_css_failure:
                self.phase = Phase.ROUTINE_CHECKS

    elif self.phase == Phase.ROUTINE_CHECKS:
        match self.step:
            case Steps.ask_sunken_contacts:
                if resp.lower() == 'na':
                    self.step = Steps.check_liquid_damage if not self.is_mopper else Steps.ask_blower_play
                elif resp:
                    self.step = Steps.sunken_ask_side
                else:
                    self.add_step('Contacts don\'t feel sunken')
                    self.step = Steps.check_liquid_damage if not self.is_mopper else Steps.ask_blower_play

            case Steps.check_liquid_damage:
                if resp.lower() == 'na':
                    self.step = Steps.ask_blower_play
                elif resp:
                    self.add_step('Found signs of liquid residue', bullet='!')
                    self.step = Steps.liquid_check_corrosion
                else:
                    self.add_step('No signs of liquid damage')
                    self.step = Steps.ask_blower_play

            case Steps.ask_blower_play:
                if resp.lower() != 'na':
                    if resp:
                        self.add_step('Found play in the blower motor', bullet='!')
                    else:
                        self.add_step('No play in blower motor')

                if self.is_combo:
                    self.step = Steps.ask_bin_rust
                else:
                    next_step = 'cleaning/lid pins'

            case Steps.ask_bin_rust:
                if not resp:
                    self.add_step('Tank float screw has no signs of rust')
                else:
                    match resp.strip():
                        case '1':
                            self.add_step('Tank float screw has a spot of rust on it', bullet='!')
                        case '2':
                            self.add_step('Tank float screw is entirely rusted', bullet='!')
                        case _:
                            return

                next_step = 'cleaning/lid pins'

            # TODO: extend this in the future to go into swap
            case Steps.ask_s9_lid_pins:
                if resp:
                    self.add_step('Lid pins are sunken', bullet='!')
                self.step = Steps.ask_cleaned

            case Steps.ask_cleaned:
                if resp.lower() != 'na':
                    self.add_step('Cleaned robot' + ((' - ' + resp) if resp else ''))

                self.step = Steps.ask_rollers

            case Steps.ask_rollers:
                if resp and resp.lower() != 'na':
                    self.add_step('Extractors are bad', bullet='!')

                if self.dock:
                    self.step = Steps.ask_user_base_contacts
                else:
                    next_step = 'battery_test/charging'

            case Steps.ask_user_base_contacts:
                if resp.lower() != 'na':
                    self.add_step(f"Charging contacts on the customer's {self.dock} look {'bad' if resp else 'good'}", bullet='!' if resp else '*')

                next_step = 'battery_test/charging'

            case Steps.battery_test:
                if resp.lower() != 'na':
                    charge, health = resp.split(',')
                    self.add_step(f'Tested battery: {charge.strip()}%/{health.strip()}%', bullet='!' if float(health.strip()) < 80 else '*')

                next_step = 'charging'

            case Steps.ask_charge_customer_dock | Steps.ask_charge_test_dock:
                if resp.lower() != 'na':
                    try:
                        watts = round(float(resp))
                    except ValueError:
                        if resp:
                            self.add_step(resp)
                            self.step = Steps.add_step
                            self.phase = Phase.DEBUGGING
                        return

                    dock = f'customer {self.dock}' if self.dock else 'test base'

                    if watts < 3:
                        self.add_step(f"Robot does not charge on {dock} @ ~{watts}W", bullet='!')
                    elif watts < 10:
                        self.add_step(f"Robot charges on {dock} @ ~{watts}W (battery is full)")
                    else:
                        self.add_step(f"Robot charges on {dock} @ ~{watts}W")

                self.step = Steps.add_step
                self.phase = Phase.DEBUGGING

            # Liquid damage path
            case Steps.liquid_check_corrosion:
                if resp.lower() != 'na':
                    if resp:
                        self.add_step(f'Found signs of liquid corrosion on the {resp}', bullet='***')
                        self._liquid_swap = True
                    else:
                        self.add_step('No signs of liquid damage on the main board or connections', bullet='***')

                next_step = 'liquid check dock or bin'

            case Steps.liquid_check_dock:
                if resp.lower() != 'na':
                    if resp:
                        self.add_step(f'Liquid residue found in the user {self.dock}', bullet='***')
                    else:
                        self.add_step(f'No signs of liquid residue found in the user {self.dock}', bullet='***')
                self.step = Steps.liquid_check_bin

            case Steps.liquid_check_bin:
                if resp.lower() != 'na':
                    if resp:
                        self.add_step('Liquid residue found in customer bin: probably sucked up liquid', bullet='***')
                    else:
                        self.add_step('No liquid residue found in customer bin', bullet='***')
                self.step = Steps.liquid_take_pictures

            # TODO connect to finish phase
            case Steps.liquid_take_pictures:
                if self._liquid_swap:
                    self.add_step('Diagnosis: Liquid damage')
                    self.add_step('Swap robot')
                    # self.phase = Phase.FINISH
                    self.step = Steps.add_step
                    self.phase = Phase.SWAP
                else:
                    # If there's liquid residue, but not on the main board, proceed
                    self.step = Steps.ask_sunken_contacts

            # Sunken contacts path
            case Steps.sunken_ask_side:
                self._sunken_side = 'right' if resp.lower() == 'r' else 'left'
                self.step = Steps.sunken_ask_measurement

            # TODO connect to finish phase
            case Steps.sunken_ask_measurement:
                try:
                    measurement = float(resp)
                except ValueError:
                    # Don't change the step, try again until we get a float
                    return

                self.add_step(f'Measured {self._sunken_side} contact: {resp}mm +/- .1')

                if measurement < 3.8:
                    self.add_step(f'Diagnosis: Sunken {self._sunken_side} contact')
                    self.add_step('Swap robot' + (f' and customer {self.dock}' if self.dock else ''))
                    self.step = Steps.add_step
                    self.phase = Phase.FINISH

                self.step = Steps.check_liquid_damage

    elif self.phase == Phase.DEBUGGING:
        match self.step:
            case Steps.add_step:
                if resp:
                    if 'Process:' not in self.text_area.text:
                        self.text_area.text = self.text_area.text.strip() + '\n\nProcess:\n'
                    self.add_step(resp[0].upper() + resp[1:])

    elif self.phase == Phase.FINISH:
        match self.step:
            case Steps.ask_final_cleaned:
                self.step = Steps.ask_base_cleaned if self.dock else Steps.ask_emptied_bin

            case Steps.ask_base_cleaned:
                self.step = Steps.ask_dock_has_bag if self.is_dock else Steps.ask_emptied_bin

            case Steps.ask_dock_has_bag:
                self.step = Steps.ask_emptied_dock if self.dock.lower() in ('aurora', 'boulder') else Steps.ask_emptied_bin

            case Steps.ask_emptied_dock:
                self.step = Steps.ask_emptied_bin

            case Steps.ask_emptied_bin:
                self.step = Steps.ask_emptied_tank if self.is_mopper else Steps.ask_sidebrush

            case Steps.ask_emptied_tank:
                self.step = Steps.ask_has_pad

            case Steps.ask_has_pad:
                self.step = Steps.ask_sidebrush

            case Steps.ask_sidebrush:
                self.step = Steps.ask_tight_screws

            case Steps.ask_tight_screws:
                self.step = Steps.ask_debug_cover

            case Steps.ask_debug_cover:
                self.step = Steps.generate_external_notes_1

            case Steps.generate_external_notes_1:
                self.external_notes_menu.visible = True
                self.step = Steps.generate_external_notes_2

            case Steps.generate_external_notes_2:
                self.step = Steps.ask_double_check

            case Steps.ask_double_check:
                self.step = Steps.ask_shipping_mode

            case Steps.ask_shipping_mode:
                self.step = Steps.ask_close_parts

            case Steps.ask_close_parts:
                self.step = Steps.ask_tags_off

            case Steps.ask_tags_off:
                self.step = Steps.ask_put_bin_back

            case Steps.ask_put_bin_back:
                self.step = Steps.ask_complete_case_CSS

            case Steps.ask_complete_case_CSS:
                self.step = Steps.ask_put_bot_on_shelf

            case Steps.ask_put_bot_on_shelf:
                self.step = Steps.finish_case

            case Steps.finish_case:
                pass
                # self.parent().parent().parent().action_close_case()

    elif self.phase == Phase.SWAP:
        match self.step:
            case Steps.swap_unuse_parts:
                self.step = Steps.swap_email

            case Steps.swap_email:
                self.step = Steps.swap_order

            case Steps.swap_order:
                self.step = Steps.swap_move_bin

            case Steps.swap_move_bin:
                if resp:
                    self.add_step('Moved bin to new robot')
                self.step = Steps.swap_note_serial

            case Steps.swap_note_serial:
                self.phase = Phase.DEBUGGING

            case _:
                pass

    # To simplify repeated next step logic
    match next_step:
        case 'battery_test/charging':
            if ('charg' in self.customer_states.lower() or 'batt' in self.customer_states.lower()) and self.dock:
                self.step = Steps.battery_test
            else:
                self.step = Steps.ask_charge_customer_dock if self.dock else Steps.ask_charge_test_dock
        case 'charging':
            self.step = Steps.ask_charge_customer_dock if self.dock else Steps.ask_charge_test_dock
        case 'liquid check dock or bin':
            self.step = Steps.liquid_check_dock if self.dock else Steps.liquid_check_bin
        case 'cleaning/lid pins':
            if self.serial.lower().startswith('s'):
                self.step = Steps.ask_s9_lid_pins
            else:
                self.step = Steps.ask_cleaned

    self.text_area.scroll_to(None, 1000, animate=False)
