import re
from clipboard import copy
from textual.containers import *
from textual.widgets import *
from Phase import Phase
from texts import Steps
from multi_paste import multi_paste
from numpy import mean, std


def execute_step(self, resp):
    # To simplify some of the redundant next step logic
    next_step = None

    # TODO: I think back isn't working
    if resp.lower() == 'back' and self.step != Steps.confirm_id:
        self.step = self.prev_step
        return

    if self.step == Steps.manual_get_serial:
        # If we accidentally pressed the change serial binding
        if resp.lower() == 'na':
            self.step = self._step_after_manual_serial

        if resp:
            self.serial = resp.lower()
            self.sidebar.serial = self.serial.lower()
            self.step = self._step_after_manual_serial
        return

    if self.phase == Phase.CONFIRM:
        match self.step:
            # Main path
            case Steps.confirm_id:
                # If we (somehow) already have the serial number, we don't need to confirm it
                if self.serial:
                    self.step = Steps.ask_labels
                    return

                ids=  resp.lower()
                if not resp:
                    # If they don't put anything, assume we aren't comparing serial numbers, and we just want to input one
                    self.ensure_serial(Steps.ask_labels)
                    return
                else:
                    if len(ids) % 2:
                        self.text_area.text = self.step = '!!! Serial numbers are different lengths !!!'
                        self.phase = Phase.FINISH
                        return
                    else:
                        half = len(ids)//2
                        if ids[half:] != ids[:half]:
                            self.text_area.text = self.step = f'!!! Serial numbers are different !!!\n{ids[half:]}\n{ids[:half]}'
                            self.phase = Phase.FINISH
                            return
                    self.serial = ids[len(resp)//2:].lower()
                    # Fill in all the info now that we have the serial number
                    self.sidebar.serial = self.serial
                    self.step = Steps.ask_labels

            case Steps.ask_labels:
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
                self.step = Steps.ask_came_with_bag if self.is_dock else Steps.customer_states

            case Steps.ask_came_with_bag:
                if resp:
                    self.text_area.text = self.text_area.text.strip() + ', no evac bag\n'
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
                    next_step = 'liquid damage'
                elif resp:
                    self.step = Steps.sunken_ask_side
                else:
                    self.add_step('Contacts don\'t feel sunken')
                    next_step = 'liquid damage'

            case Steps.ask_modular:
                if resp:
                    self.add_step('Robot is non-modular')
                    self._modular = False
                    # Update the sidebar, cause DCT is different for modular models
                    self.sidebar.update_dct()
                    self.step = Steps.ask_cleaned
                else:
                    # We don't need to confirm that it's not a mopper here; there are no i-series moppers
                    self.step = Steps.check_liquid_damage

            case Steps.check_liquid_damage:
                if resp.lower() == 'na':
                    next_step = 'ask blower play'
                elif resp:
                    self.add_step('Found signs of liquid residue', bullet='!')
                    self.step = Steps.liquid_check_corrosion
                    self._liquid_found = True
                else:
                    self.add_step('No signs of liquid residue')
                    next_step = 'ask blower play'

            case Steps.ask_blower_play:
                if resp.lower() != 'na':
                    if resp:
                        self.add_step('Found play in the blower motor', bullet='!')
                    else:
                        self.add_step('No play in the blower motor, and it spins freely')

                next_step = 'post blower play'

            case Steps.ask_bin_rust:
                if not resp:
                    self.add_step('Tank float screw has no signs of rust')
                else:
                    match resp.strip():
                        case '1':
                            self.add_step('Tank float screw has a spot of rust on it', bullet='!')
                            self._bin_screw_has_rust = True
                        case '2':
                            self.add_step('Tank float screw is entirely rusted', bullet='!')
                            self._bin_screw_has_rust = True
                        case _:
                            return

                next_step = 'cleaning/lid pins'

            case Steps.ask_dock_tank_rust:
                if not resp:
                    self.add_step('Dock tank float screw has no signs of rust')
                else:
                    match resp.strip():
                        case '1':
                            self.add_step('Dock tank float screw has a spot of rust on it', bullet='!')
                            self._dock_tank_screw_has_rust = True
                        case '2':
                            self.add_step('Dock tank float screw is entirely rusted', bullet='!')
                            self._dock_tank_screw_has_rust = True
                        case _:
                            return

                # This is next_step = 'cleaning/lid pins', except not recursive
                if self.serial.lower().startswith('s'):
                    self.step = Steps.ask_s9_lid_pins
                else:
                    self.step = Steps.ask_cleaned

            # TODO: extend this in the future to go into swap
            case Steps.ask_s9_lid_pins:
                if resp:
                    self.add_step('Lid pins are sunken', bullet='!')
                    self.phase = Phase.SWAP
                else:
                    self.add_step('Lid pins don\'t appear sunken')
                self.step = Steps.ask_cleaned

            case Steps.ask_cleaned:
                if resp.lower() != 'na':
                    self.add_step('Cleaned robot' + ((' - ' + resp) if resp else ''))

                if self.can_vacuum:
                    self.step = Steps.ask_rollers
                else:
                    next_step = 'dock contacts/charging'

            case Steps.ask_rollers:
                if resp.lower() != 'na':
                    self.add_step('Extractors look ' + (resp if resp else 'good'), bullet='!' if resp else '*')

                next_step = 'dock contacts/charging'

            case Steps.ask_user_base_contacts:
                if resp.lower() != 'na':
                    self.add_step(f"Charging contacts on the customer's {self.dock} look {resp or 'good'}")

                next_step = 'battery_test/charging'

            case Steps.battery_test:
                if resp.lower() != 'na':
                    # charge, health = resp.split(',')
                    try:
                        charge, health = re.split(r'(?:,|\s)(?:\s)?', resp)
                    except ValueError: return
                    self.add_step(f'Tested battery: {charge.strip()}%/{health.strip()}%', bullet='!' if float(health.strip()) < 80 else '*')

                if self._swap_after_battery_test:
                    self.phase = Phase.SWAP
                else:
                    next_step = 'charging'

            case Steps.ask_charge_customer_dock | Steps.ask_charge_test_dock:
                if resp.lower() != 'na':
                    try:
                        watts = round(float(resp))
                    except ValueError:
                        if resp:
                            self.add_step(resp)
                            self.phase = Phase.DEBUGGING
                        return

                    dock = f'customer {self.dock}' if self.dock else 'test base'

                    if watts < 3:
                        self.add_step(f"Robot does not charge on {dock} @ ~{watts}W", bullet='!')
                    elif watts < 10:
                        self.add_step(f"Robot charges on {dock} @ ~{watts}W (battery is full)")
                    else:
                        self.add_step(f"Robot charges on {dock} @ ~{watts}W")

                self.phase = Phase.DEBUGGING

            # Liquid damage path
            case Steps.liquid_check_corrosion:
                if resp.lower() != 'na':
                    if resp:
                        self.add_step(f'Found signs of liquid corrosion on the {resp}', bullet='**')
                        self._liquid_swap = True
                    else:
                        self.add_step('No signs of liquid damage on the main board or connections', bullet='**')

                next_step = 'liquid check dock or bin'

            case Steps.liquid_check_dock:
                if resp.lower() != 'na':
                    if resp:
                        self.add_step(f'Liquid residue found in the user {self.dock}', bullet='**')
                    else:
                        self.add_step(f'No signs of liquid residue found in the user {self.dock}', bullet='**')
                self.step = Steps.liquid_check_bin

            case Steps.liquid_check_bin:
                if resp.lower() != 'na':
                    if resp:
                        self.add_step('Liquid residue found in customer bin: probably sucked up liquid', bullet='**')
                    else:
                        self.add_step('No liquid residue found in customer bin', bullet='**')
                self.step = Steps.liquid_take_pictures

            case Steps.liquid_take_pictures:
                if self._liquid_swap:
                    self.ensure_process()
                    self.add_step('Diagnosis: Liquid damage')
                    self.add_step('Swap robot')
                    self.phase = Phase.SWAP
                else:
                    # If there's liquid residue, but not on the main board, proceed
                    self.step = Steps.ask_sunken_contacts

            # Sunken contacts path
            case Steps.sunken_ask_side:
                match resp.lower():
                    case 'r': self.step = Steps.sunken_ask_right_measurement
                    case 'l': self.step = Steps.sunken_ask_left_measurement
                    case 'b':
                        self._also_check_left = True
                        self.step = Steps.sunken_ask_right_measurement

            case Steps.sunken_ask_right_measurement:
                try:
                    # either(',', whitespace) + optional(whitespace)
                    measurements = list(map(float, re.split(r'(?:,|\s)(?:\s)?', resp)))
                except ValueError:
                    # Keep what's already there, but don't submit it if it's wrong
                    self.input.value = resp
                    return

                self.add_step(f'Measured right contact: {mean(measurements):.1f}mm +/- {std(measurements) or .1:.1f}')

                if mean(measurements) < 3.8:
                    self.ensure_process()
                    self.add_step('Sunken right contact')
                    self.add_step('Swap robot' + (f' and customer {self.dock}' if self.dock else ''))
                    self._swap_after_battery_test = True
                    next_step = 'battery_test/charging'
                    # self.phase = Phase.SWAP
                elif self._also_check_left:
                    self.step = Steps.sunken_ask_left_measurement
                else:
                    next_step = 'liquid damage'

            case Steps.sunken_ask_left_measurement:
                try:
                    # either(',', whitespace) + optional(whitespace)
                    measurements = list(map(float, re.split(r'(?:,|\s)(?:\s)?', resp)))
                except ValueError:
                    # Keep what's already there, but don't submit it if it's wrong
                    self.input.value = resp
                    return

                self.add_step(f'Measured left contact: {mean(measurements):.1f}mm +/- {round(std(measurements), 1) or .1:.1f}')

                if mean(measurements) < 3.8:
                    self.ensure_process()
                    self.add_step('Sunken left contact')
                    self.add_step('Swap robot' + (f' and customer {self.dock}' if self.dock else ''))
                    self._swap_after_battery_test = True
                    next_step = 'battery_test/charging'
                    # self.phase = Phase.SWAP
                else:
                    next_step = 'liquid damage'

    elif self.phase == Phase.DEBUGGING:
        match self.step:
            case Steps.add_step:
                if resp:
                    self.add_step(resp[0].upper() + resp[1:])
                else:
                    self.ensure_process()

    elif self.phase == Phase.FINISH:
        match self.step:
            case Steps.generate_external_notes:
                self.external_notes_menu.visible = False
                copy(self.text_area.text.strip())
                self._finish_first_copy_notes = self.text_area.text.strip()
                self.step = Steps.ask_copy_notes_1

            case Steps.ask_copy_notes_1:
                multi_paste(
                    'michelle.gonzalez@acer.com',
                    f'Double Check: {self.ref}',
                    self.text_area.text,
                )
                self.step = Steps.ask_double_check

            case Steps.ask_double_check:
                self.step = Steps.ask_final_cleaned

            case Steps.ask_final_cleaned:
                if self.dock:
                    self.step = Steps.ask_base_cleaned
                else:
                    next_step = 'empty bin'

            case Steps.ask_base_cleaned:
                if self.is_dock:
                    self.step = Steps.ask_dock_has_bag
                else:
                    next_step = 'empty bin'

            case Steps.ask_dock_has_bag:
                if self.dock_can_refill:
                    self.step = Steps.ask_emptied_dock
                else:
                    next_step = "empty bin"

            case Steps.ask_emptied_dock:
                # It's okay to not ask if it can vacuum here, cause an M6 isn't gonna have an Aurora or Boulder dock with it
                self.step = Steps.ask_emptied_bin

            case Steps.ask_emptied_bin:
                next_step = "empty tank"

            case Steps.ask_emptied_tank:
                self.step = Steps.ask_does_not_have_pad if self.serial.startswith('m6') else Steps.ask_has_pad

            case Steps.ask_does_not_have_pad:
                self.step = Steps.ask_debug_cover

            case Steps.ask_has_pad:
                self.step = Steps.ask_debug_cover

            case Steps.ask_debug_cover:
                self.step = Steps.ask_sidebrush_screws

            case Steps.ask_sidebrush_screws:
                self.step = Steps.double_check_confirmed

            case Steps.double_check_confirmed:
                self.step = Steps.ask_shipping_mode

            case Steps.ask_shipping_mode:
                self.step = Steps.ask_close_parts

            case Steps.ask_close_parts:
                self.step = Steps.ask_tags_off

            case Steps.ask_tags_off:
                self.step = Steps.ask_put_bin_back

            case Steps.ask_put_bin_back:
                # If the notes haven't changed since we last updated CSS, we don't need to update CSS again
                if self._finish_first_copy_notes == self.text_area.text.strip():
                    multi_paste(
                        self.ref,
                        'Repair Report',
                    )
                    self.step = Steps.ask_complete_case_CSS
                else:
                    copy(self.text_area.text.strip())
                    self.step = Steps.ask_copy_notes_2

            case Steps.ask_copy_notes_2:
                multi_paste(
                    self.ref,
                    'Repair Report',
                )
                # copy(self.ref)
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
                copy(self.text_area.text.strip())
                self.step = Steps.swap_update_css

            case Steps.swap_update_css:
                multi_paste(
                    'irobot.support@acer.com',
                    self.ref + ' - ',
                    self.text_area.text,
                )
                # copy(self.ref + ' - ')
                self.step = Steps.swap_email

            case Steps.swap_email:
                if self.serial.startswith('s9'):
                    self.step = Steps.swap_order_S9
                elif self.serial.startswith('m6'):
                    self.step = Steps.swap_order_M6
                else:
                    copy(self.serial.upper())
                    self.step = Steps.swap_order

            case Steps.swap_order_S9:
                self.step = Steps.swap_put_in_box

            case Steps.swap_order_M6:
                self.step = Steps.swap_put_in_box

            case Steps.swap_order:
                self.step = Steps.swap_move_bin

            case Steps.swap_move_bin:
                if resp:
                    self.add_step('Moved bin to new robot')
                self.step = Steps.swap_put_in_box

            case Steps.swap_put_in_box:
                self.step = Steps.swap_note_serial

            case Steps.swap_note_serial:
                self.phase = Phase.DEBUGGING

            case _:
                pass

    # To simplify repeated next step logic
    if next_step == 'dock contacts/charging':
        if self.dock:
            self.step = Steps.ask_user_base_contacts
        else:
            next_step = 'battery_test/charging'

    if next_step == 'battery_test/charging':
        if 'charg' in self.customer_states.lower() or 'batt' in self.customer_states.lower() or self._liquid_found:
            self.step = Steps.battery_test
        elif self._swap_after_battery_test:
            self.phase = Phase.SWAP
        else:
            next_step = 'charging'

    if next_step == 'charging':
        self.step = Steps.ask_charge_customer_dock if self.dock else Steps.ask_charge_test_dock

    if next_step == 'liquid check dock or bin':
        self.step = Steps.liquid_check_dock if self.dock else Steps.liquid_check_bin

    if next_step == 'ask blower play':
        if self.can_vacuum:
            self.steps = Steps.ask_blower_play
        else:
            next_step = 'post blower play'

    if next_step == 'post blower play':
        if self.is_combo:
            self.step = Steps.ask_bin_rust
        else:
            next_step = 'cleaning/lid pins'

    if next_step == 'cleaning/lid pins':
        if self.dock_can_refill:
            self.step = Steps.ask_dock_tank_rust
        elif self.serial.lower().startswith('s'):
            self.step = Steps.ask_s9_lid_pins
        else:
            self.step = Steps.ask_cleaned

    if next_step == 'liquid damage':
        if self.serial.startswith('i'):
            self.step = Steps.ask_modular
        else:
            self.step = Steps.check_liquid_damage if not self.can_mop else Steps.ask_blower_play

    if next_step == 'empty bin':
        if self.can_vacuum:
            self.step = Steps.ask_emptied_bin
        else:
            next_step = 'empty tank'

    if next_step == 'empty tank':
        self.step = Steps.ask_emptied_tank if self.can_mop else Steps.ask_debug_cover

    self.text_area.scroll_to(None, 1000, animate=False)
