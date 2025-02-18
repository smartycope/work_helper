import re
from textual.containers import *
from textual.widgets import *
from Phase import Phase
from globals import capitolize
from parse_commands import parse_acronym
from texts import Steps
from numpy import mean, std
import settings
import clipboard
import settings
from multi_paste import multi_paste


def execute_step(self, resp):
    # To simplify some of the redundant next step logic
    next_step = None
    resp = resp.strip()

    # This step specifically does parses them itself later, after it parses the commands
    if self.step != Steps.add_step:
        resp = parse_acronym(resp)

    # TODO: I think back isn't working
    if resp.lower() == 'back' and self.step != Steps.confirm_id:
        self.step = self.prev_step
        return

    if self.step == Steps.manual_get_serial:
        # If we accidentally pressed the change serial binding
        if resp.lower() == 'na':
            self.step = self._step_after_manual_serial

        if resp:
            self.add_serial(resp.lower())
            self.step = self._step_after_manual_serial
        return


    if self.phase == Phase.CONFIRM:
        match self.step:
            # Main path
            case Steps.confirm_id:
                # If we (somehow) already have the serial number, we don't need to confirm it
                if self.serial:
                    self.step = Steps.turn_down_screwdriver if self.serial.startswith('m6') else Steps.ask_labels
                    return

                if not resp:
                    # If they don't put anything, assume we aren't comparing serial numbers, and we just want to input one
                    self.ensure_serial(Steps.ask_labels)
                    return
                else:
                    ids=  resp.lower()
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
                    self.add_serial(ids[len(resp)//2:])
                    self.step = Steps.turn_down_screwdriver if self.serial.startswith('m6') else Steps.ask_labels

            case Steps.turn_down_screwdriver:
                self.step = Steps.ask_labels

            case Steps.ask_labels:
                self.step = Steps.check_repeat

            case Steps.check_repeat:
                self.repeat = bool(resp)
                self.step = Steps.check_claimed_damage

            case Steps.check_claimed_damage:
                self.step = Steps.pick_up_case

            case Steps.pick_up_case:
                self.step = Steps.ask_dock

            case Steps.ask_dock:
                self._dock = self.snap_to_dock(resp)
                self.text_area.text += 'Parts in: ' + self.serial.upper()
                if resp:
                    self.text_area.text += ', ' + resp + ', cord'
                self.text_area.text += '\n'
                self.step = Steps.ask_damage

            case Steps.ask_damage:
                self.text_area.text += 'Damage: Minor scratches'
                if resp:
                    self.text_area.text += ', ' + capitolize(resp)
                self.text_area.text += '\n'
                if self.is_dock:
                    self.step = Steps.ask_came_with_bag
                else:
                    next_step = "ask pad"

            case Steps.ask_came_with_bag:
                if resp and resp != 'na':
                    self.text_area.text = self.text_area.text.strip() + ', no evac bag\n'
                    self.sidebar.todo.text += '\norder evac bag'
                next_step = 'ask pad'

            case Steps.ask_came_with_pad:
                if resp and resp != 'na':
                    self.text_area.text = self.text_area.text.strip() + ', no pad\n'
                    self.sidebar.todo.text += '\norder pad'
                self.step = Steps.customer_states

            case Steps.customer_states:
                if resp:
                    self._customer_states = capitolize(resp)
                    self.text_area.text += 'Customer States: ' + self.customer_states + '\n\nRoutine Checks:\n'
                    if not self.is_modular:
                        self.add_step('Robot is non-modular')
                    self.step = Steps.update_css_failure

            case Steps.update_css_failure:
                self.phase = Phase.ROUTINE_CHECKS

    elif self.phase == Phase.ROUTINE_CHECKS:
        match self.step:
            case Steps.ask_sunken_contacts:
                if resp.lower() == 'na':
                    next_step = 'liquid damage'
                elif resp:
                    match resp.lower():
                        case 'r': self.step = Steps.sunken_ask_right_measurement
                        case 'l': self.step = Steps.sunken_ask_left_measurement
                        case 'b':
                            self._also_check_left = True
                            self.step = Steps.sunken_ask_right_measurement
                else:
                    self.add_step('Contacts don\'t feel sunken')
                    next_step = 'liquid damage'

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
                if resp.lower() == 'na':
                    pass
                elif not resp:
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

            case Steps.ask_quiet_audio:
                if resp:
                    self.add_step('Audio is noticeably quiet - suspect The Glitch', '!')
                else:
                    self.add_step('Audio does not seem quiet')
                self.phase = Phase.DEBUGGING

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
                    self.add_step('Extractors look ' + (resp if resp else 'fine'), bullet='!' if resp else '*')

                next_step = 'dock contacts/charging'

            case Steps.ask_user_base_contacts:
                if resp.lower() != 'na':
                    self.add_step(f"Charging contacts on the customer's {self.dock} look {resp or 'fine'}", '!' if resp else '*')

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
                            next_step = 'quiet audio'
                        return

                    dock = f'cx {self.dock}' if self.dock else 'test base'

                    if watts < 3:
                        self.add_step(f"Robot does not charge on {dock} @ ~{watts}W", bullet='!')
                    elif watts < 10:
                        self.add_step(f"Robot charges on {dock} @ ~{watts}W (battery is full)")
                    else:
                        self.add_step(f"Robot charges on {dock} @ ~{watts}W")

                next_step = 'quiet audio'

            # Liquid damage path
            case Steps.liquid_check_corrosion:
                if resp.lower() != 'na':
                    if resp:
                        self.add_step(f'Found signs of liquid corrosion on the {"main board" if resp.lower() in ('y', 'yes') else resp}', bullet='**')
                        self._liquid_swap = True
                    else:
                        self.add_step('No signs of liquid damage on the main board or connections', bullet='**')

                next_step = 'liquid check dock or bin'

            case Steps.liquid_check_dock:
                if resp.lower() != 'na':
                    if resp:
                        self.add_step(f'Liquid residue found in the cx {self.dock}', bullet='**')
                    else:
                        self.add_step(f'No signs of liquid residue found in the cx {self.dock}', bullet='**')
                self.step = Steps.liquid_check_bin

            case Steps.liquid_check_bin:
                if resp.lower() != 'na':
                    if resp:
                        self.add_step('Liquid residue found in cx bin: probably sucked up liquid', bullet='**')
                    else:
                        self.add_step('No liquid residue found in cx bin', bullet='**')
                if self.dock:
                    self.step_formatter = '2.8' if self.is_dock else '3.2'
                    self.step = Steps.liquid_check_voltage
                else:
                    self.step = Steps.liquid_take_pictures

            case Steps.liquid_check_voltage:
                if resp and resp.lower() != 'na':
                    try:
                        volts = float(resp)
                    except ValueError: return

                    self.add_step(f'Measured voltage across cx {self.dock}: {volts}V', '**')
                # TODO:
                elif not resp:
                    pass

                self.step = Steps.liquid_take_pictures

            case Steps.liquid_take_pictures:
                if self._liquid_swap:
                    self.ensure_process()
                    self.add_step('Diagnosis: Liquid damage')
                    self.add_step('Swap robot')
                    self.phase = Phase.SWAP
                else:
                    # If there's liquid residue, but not on the main board, proceed
                    # self.step = Steps.ask_sunken_contacts
                    next_step = 'ask blower play'

            # Sunken contacts path
            case Steps.sunken_ask_right_measurement:
                try:
                    # either(',', whitespace) + optional(whitespace)
                    measurements = list(map(float, re.split(r'(?:,|\s)(?:\s)?', resp)))
                except ValueError:
                    # Keep what's already there, but don't submit it if it's wrong
                    self.input.value = resp
                    return

                meas = mean(measurements)
                meas = round(meas, 1 if 3.8 > meas > 3.74 else 2)
                self.add_step(f'Measured right contact: {meas}mm +/- {max(std(measurements), .1):.1f}', '*' if meas > 3.8 else '!')

                if mean(measurements) < 3.8:
                    self.ensure_process()
                    self.add_step('Sunken right contact')
                    self.add_step('Swap robot and ' + (f'cx {self.dock}' if self.dock else 'ordering a new dock'))
                    self._swap_after_battery_test = True
                    self._swap_due_to_sunken_contacts = True
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
                    self.add_step('Swap robot' + (f' and cx {self.dock}' if self.dock else ''))
                    self._swap_after_battery_test = True
                    self._swap_due_to_sunken_contacts = True
                    next_step = 'battery_test/charging'
                    # self.phase = Phase.SWAP
                else:
                    next_step = 'liquid damage'

    elif self.phase == Phase.DEBUGGING:
        match self.step:
            case Steps.add_step:
                if resp:
                    self.parse_command(resp)
                else:
                    self.ensure_process()

    elif self.phase == Phase.FINISH:
        match self.step:
            case Steps.ask_bit_mobility_done:
                # lapis and m6 are mutually exclusive
                if self.has_lapis or self.is_factory_lapis or self.has_weird_i5g:
                    self.step = Steps.ask_lapis_mobility_done
                elif self.serial.startswith('m6'):
                    self.step = Steps.ask_m6_dry_mobility
                else:
                    self.step = Steps.generate_external_notes
                    self.external_notes_menu.action_open()

            case Steps.ask_lapis_mobility_done | Steps.ask_m6_dry_mobility:
                self.step = Steps.generate_external_notes

            case Steps.generate_external_notes:
                self.step = Steps.ask_close_parts

            case Steps.ask_close_parts:
                if settings.DO_DOUBLE_CHECK:
                    self.step = Steps.ask_double_check
                else:
                    self.step = Steps.ask_shipping_mode

            case Steps.ask_double_check:
                self.step = Steps.ask_shipping_mode

            case Steps.ask_shipping_mode:
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
                self.step = Steps.ask_sidebrush_screws

            case Steps.ask_has_pad:
                self.step = Steps.ask_sidebrush_screws

            case Steps.ask_sidebrush_screws:
                self.step = Steps.double_check_confirmed if settings.DO_DOUBLE_CHECK else Steps.ask_tags_off

            case Steps.double_check_confirmed:
                self.step = Steps.ask_tags_off

            case Steps.ask_tags_off:
                # self.step = Steps.ask_put_bin_back

            # case Steps.ask_put_bin_back:
                # If the notes haven't changed since we last updated CSS, we don't need to update CSS again
                if self._finish_first_copy_notes == self.text_area.text.strip():
                    self.step = Steps.wait_parts_closed
                else:
                    self.step = Steps.ask_copy_notes_2

            case Steps.ask_copy_notes_2:
                self.step = Steps.wait_parts_closed

            case Steps.wait_parts_closed:
                self.step = Steps.ask_complete_case_CSS

            case Steps.ask_complete_case_CSS:
                if self.repeat:
                    self.step = Steps.ask_submit_adj
                else:
                    next_step = 'put on shelf'

            case Steps.ask_submit_adj:
                next_step = 'put on shelf'

            case Steps.ask_put_bot_on_shelf | Steps.ask_put_bot_on_shelf_mopping:
                self.step = Steps.finish_case

            case Steps.finish_case:
                pass
                # self.parent().parent().parent().action_close_case()

    elif self.phase == Phase.SWAP:
        match self.step:
            case Steps.swap_unuse_parts:
                self.step = Steps.swap_update_css

            case Steps.swap_update_css:
                self.step = Steps.swap_email

            case Steps.swap_email:
                if self._swap_due_to_sunken_contacts:
                    self.step = Steps.swap_order_dock
                else:
                    next_step = 'order swap'

            case Steps.swap_order_dock:
                if resp.lower() == 'out':
                    self.phase = Phase.HOLD

                next_step = 'order swap'

            case Steps.swap_order_S9:
                if resp.lower() == 'out':
                    self.phase = Phase.HOLD
                self.step = Steps.swap_ask_refurb

            case Steps.swap_order_M6:
                if resp.lower() == 'out':
                    self.phase = Phase.HOLD
                self.step = Steps.swap_ask_refurb

            case Steps.swap_order:
                self.step = Steps.swap_move_bin

            case Steps.swap_move_bin:
                if resp:
                    self.add_step('Moved bin to new robot')
                self.step = Steps.swap_ask_refurb

            case Steps.swap_ask_refurb:
                self._is_current_swap_refurb = not bool(resp)
                if not self._is_current_swap_refurb:
                    self.add_step('BiT: skipping, as the swapped bot is a non-refurb')
                self.step = Steps.swap_add_labels

            case Steps.swap_add_labels:
                self.step = Steps.swap_input_new_serial

            case Steps.swap_input_new_serial:
                if resp:
                    self.add_serial(resp)
                    # '*' + at_most(2, anything) + IGNORECASE + 'swap' + at_most(8, anything) + 'bot' + optional(chunk)
                    last: re.Match = list(re.finditer(r'(?i)\*.{0,2}swap.{0,8}bot(?:.+)?', self.text_area.text))[-1]
                    t = self.text_area.text.strip()
                    self.text_area.text = t[:last.end()] + f' -> {resp} ({"" if self._is_current_swap_refurb else "non-"}refurb)' + t[last.end():]
                    self.step = Steps.swap_note_serial

            case Steps.swap_note_serial:
                self.phase = Phase.DEBUGGING

            case _:
                pass

    elif self.phase == Phase.HOLD:
        match self.step:
            case Steps.hold_add_context:
                self.step = Steps.hold_copy_notes_to_CSS

            case Steps.hold_copy_notes_to_CSS:
                self.step = Steps.hold_unuse_parts

            case Steps.hold_unuse_parts:
                self.step = Steps.hold_put_on_shelf

            case Steps.hold_put_on_shelf:
                self.step = Steps.hold_done

            case Steps.hold_done:
                # Don't change the step
                pass

    elif self.phase == Phase.CHARGING:
        self.phase = Phase.DEBUGGING

    elif self.phase == Phase.UPDATING:
        self.phase = Phase.DEBUGGING


    # To simplify repeated next step logic
    if next_step == "ask pad":
        self.step = Steps.ask_came_with_pad if self.is_combo else Steps.customer_states

    if next_step == 'quiet audio':
        if self.serial.startswith(('c', 'j')) and "evac" in self.customer_states.lower():
            self.step = Steps.ask_quiet_audio
        else:
            self.phase = Phase.DEBUGGING

    if next_step == 'put on shelf':
        if not self.is_dock:
            self.step_formatter = ' and box'
        self.step = Steps.ask_put_bot_on_shelf_mopping if self.can_mop else Steps.ask_put_bot_on_shelf

    if next_step == 'dock contacts/charging':
        if self.dock:
            self.step = Steps.ask_user_base_contacts
        else:
            next_step = 'battery_test/charging'

    if next_step == 'battery_test/charging':
        if self.require_battery_test():
            self.step = Steps.battery_test
        elif self._swap_after_battery_test:
            self.phase = Phase.SWAP
        else:
            next_step = 'charging'

    if next_step == 'order swap':
        if self.serial.startswith('s9'):
            self.step = Steps.swap_order_S9
        elif self.serial.startswith('m6'):
            self.step = Steps.swap_order_M6
        else:
            self.step = Steps.swap_order

    if next_step == 'charging':
        self.step = Steps.ask_charge_customer_dock if self.dock else Steps.ask_charge_test_dock

    if next_step == 'liquid check dock or bin':
        self.step = Steps.liquid_check_dock if self.dock else Steps.liquid_check_bin

    if next_step == 'liquid damage':
        if not self.is_modular:
            self.step = Steps.ask_cleaned
        else:
            if self.can_mop:
                next_step = 'ask blower play'
            else:
                self.step = Steps.check_liquid_damage

    if next_step == 'ask blower play':
        if self.can_vacuum:
            self.step = Steps.ask_blower_play
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

    if next_step == 'empty bin':
        if self.can_vacuum:
            self.step = Steps.ask_emptied_bin
        else:
            next_step = 'empty tank'

    if next_step == 'empty tank':
        self.step = Steps.ask_emptied_tank if self.can_mop else Steps.ask_sidebrush_screws

    self.text_area.scroll_to(None, 1000, animate=False)


# All the side effects of the execute_step
# Remember to import these in Case if you add a new one!
def before_pick_up_case(self):
    clipboard.copy(self.ref)

def after_pick_up_case(self):
    self.log('open')

def after_ask_complete_case_CSS(self):
    self.log('close')

def before_generate_external_notes(self):
    self.external_notes_menu.action_open()
    clipboard.copy(self.text_area.text.strip())
    self._finish_first_copy_notes = self.text_area.text.strip()

def after_generate_external_notes(self):
    self.external_notes_menu.action_close()

def before_ask_double_check(self):
    if settings.DO_DOUBLE_CHECK:
        multi_paste(
            'michelle.gonzalez@acer.com',
            f'Double Check: {self.ref}',
            self.text_area.text,
        )

def before_ask_copy_notes_2(self):
    clipboard.copy(self.text_area.text.strip())

def before_ask_complete_case_CSS(self):
    # multi_paste(
    #     self.ref,
    #     'Repair Report',
    # )
    clipboard.copy(self.ref)

def before_swap_update_css(self):
    clipboard.copy(self.text_area.text.strip())

def before_swap_email(self):
    multi_paste(
        'irobot.support@acer.com',
        self.ref + ' - ',
        self.text_area.text,
    )

def before_swap_order(self):
    clipboard.copy(self.serial.upper())

def before_swap_note_serial(self):
    clipboard.copy(self.serial.upper())

def before_hold_copy_notes_to_CSS(self):
    clipboard.copy(self.text_area.text.strip())

def before_wait_parts_closed(self):
    clipboard.copy(self.ref)
    self.log('finish')

def before_hold_add_context(self):
    self.ensure_context()
    self.text_area.text += self.sidebar.todo.text
    # I decided against this
    # self.sidebar.todo.text = ''

def before_ask_submit_adj(self):
    multi_paste(
        'michelle.gonzalez@acer.com',
        f'Adjustment: {self.ref}',
        f"{self.ref}: minutes"
    )
