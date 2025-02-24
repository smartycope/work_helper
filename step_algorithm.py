import re
from numpy import mean, std
import re
from textual.containers import *
from textual.widgets import *
from Phase import Phase
from globals import SECRET_PASSWORD, capitolize
from parse_commands import parse_acronym
from texts import Steps
import settings
import clipboard
import settings
from multi_paste import multi_paste
from datetime import datetime
from math import ceil

DO_NOT_PARSE_ACRONYM_STEPS = [
    # This step specifically does parses them itself later, after it parses the commands
    Steps.add_step,
    Steps.ask_sunken_contacts,
    Steps.battery_test,
    Steps.ask_bin_rust,
    Steps.ask_dock_tank_rust,
]

def execute_step(self, resp):
    # To simplify some of the redundant next step logic
    next_step = None

    if resp == SECRET_PASSWORD:
        self.step = Steps._debug_mode
        return

    resp = resp.strip()

    if self.step not in DO_NOT_PARSE_ACRONYM_STEPS:
        resp = parse_acronym(resp)

    if self.step == Steps._debug_mode:
        if resp:
            self.step = getattr(Steps, resp, Steps._debug_mode)
            if self.step == Steps._debug_mode:
                self.phase = getattr(Phase, resp, self.phase)
            return

    if resp.lower() == 'back' and self.step != Steps.confirm_id:
        self.step = self.prev_step
        return

    if self.step == Steps.manual_get_serial:
        # If we just deserialized, and we got left on this step, or something else wonkey happened,
        # default to this step as a precaution
        fallback = Steps.ask_labels
        # If we accidentally pressed the change serial binding
        if resp.lower() == 'na':
            self.step = self._step_after_manual_serial or fallback

        if resp:
            self.add_serial(resp.lower())
            self.step = self._step_after_manual_serial or fallback

        self._update_label()

        return

    if self.step == Steps.pick_up_case:
        self._case_picked_up = True
        self.step = Steps.confirm_id
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
                        self.text_area.text += '\n\n!!! Serial numbers are different lengths !!!'
                        # self.phase = Phase.FINISH
                        return
                    else:
                        half = len(ids)//2
                        if not self._ids_equal(ids[half:], ids[:half]):
                            self.text_area.text += f'\n\n!!! Serial numbers are different !!!\n{ids[half:]}\n{ids[:half]}'
                            # self.phase = Phase.FINISH
                            return
                    self.add_serial(ids[len(resp)//2:])
                    self._update_label()
                    self.step = Steps.turn_down_screwdriver if self.serial.startswith('m6') else Steps.ask_labels

            case Steps.turn_down_screwdriver:
                self.step = Steps.ask_labels

            case Steps.ask_labels:
                self.step = Steps.check_repeat

            case Steps.check_repeat:
                self.repeat = bool(resp)
                if self.repeat:
                    self._update_label()
                    self.sidebar.update()
                    if 'repeat' not in self.text_area.text.splitlines()[0].lower():
                        self.text_area.text = self.text_area.text.replace('\n', ' repeat of \n', 1)

                self.step = Steps.check_claimed_damage

            case Steps.check_claimed_damage:
                self.step = Steps.ask_dock

            case Steps.ask_dock:
                self._dock = self.snap_to_dock(resp)
                self.text_area.text += 'Parts in: ' + self.serial.upper()
                if resp:
                    self.text_area.text += ', ' + self._dock + ', cord'
                # We snap to all of them before, so if we specify, we want to include that. But for the rest of the program, just use Albany.
                if self._dock == 'Alex-Albany':
                    self._dock = 'Albany'
                self.text_area.text += '\n'
                self.step = Steps.ask_damage

            case Steps.ask_damage:
                self.text_area.text += 'Damage: Minor scratches'
                if resp:
                    self.text_area.text += ', ' + capitolize(resp)
                    # As a reminder, I usually have to do something about it
                    self.sidebar.todo.text += '\n' + resp
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

                if self._bin_screw_has_rust:
                    self.sidebar.todo.text += '\nOrder new bin'

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

                if self._dock_tank_screw_has_rust:
                    self.sidebar.todo.text += '\nFreebee dock tank'

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
                if not resp:
                    return

                if resp.lower() != 'na':
                    # charge, health = resp.split(',')
                    try:
                        inputs = re.split(r'(?:,|\s)(?:\s)?', resp)
                    except ValueError: return

                    if len(inputs) == 2:
                        charge, health = inputs
                    elif len(inputs) == 1:
                        charge = inputs[0]
                        health = '100'
                    else:
                        return

                    self.add_step(f'Tested battery: {charge.strip()}%/{health.strip()}%', bullet='!' if float(health.strip()) < 80 else '*')

                if self._swap_after_battery_test:
                    self.phase = Phase.SWAP
                else:
                    next_step = 'charging'

            case Steps.ask_charge_customer_dock | Steps.ask_charge_test_dock:
                if resp.lower() != 'na':
                    try:
                        watts = float(resp)
                    except ValueError:
                        if resp:
                            self.add_step(resp)
                            next_step = 'quiet audio'
                        return

                    dock = f'cx {self.dock}' if self.dock else 'test base'

                    if watts < 1:
                        self.add_step(f"Robot does not charge on {dock} @ ~{watts:.1f}W", bullet='!')
                    elif watts < 10:
                        self.add_step(f"Robot charges on {dock} @ ~{watts:.1f}W (battery is full)")
                    else:
                        self.add_step(f"Robot charges on {dock} @ ~{watts:.0f}W")

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
            # TODO: combine these into a single function
            case Steps.sunken_ask_right_measurement:
                try:
                    # either(',', whitespace) + optional(whitespace)
                    measurements = list(map(float, re.split(r'(?:,|\s)(?:\s)?', resp)))
                except ValueError:
                    # Keep what's already there, but don't submit it if it's wrong
                    self.input.value = resp
                    return

                self.add_measure_contacts_step('r', measurements)
                # meas = mean(measurements)
                # meas = round(meas, 1 if 3.8 > meas > 3.74 else 2)
                # self.add_step(f'Measured right contact: {meas}mm +/- {max(std(measurements), .1):.1f}', '*' if meas > 3.8 else '!')

                if mean(measurements) < 3.8:
                    self.ensure_process()
                    self.add_step('Diagnosis: Sunken right contact')
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

                self.add_measure_contacts_step('l', measurements)
                # self.add_step(f'Measured left contact: {mean(measurements):.1f}mm +/- {round(std(measurements), 1) or .1:.1f}')

                if mean(measurements) < 3.8:
                    self.ensure_process()
                    self.add_step('Diagnosis: Sunken left contact')
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
                    next_step = 'remove from app'

            case Steps.ask_lapis_mobility_done | Steps.ask_m6_dry_mobility:
                next_step = 'remove from app'

            case Steps.ask_removed_provisioning:
                if 'removed provisioning' not in self.text_area.text.lower():
                    self.add_step('Removed provisioning')
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
                next_step = 'screws tight'

            case Steps.ask_has_pad:
                next_step = 'screws tight'

            case Steps.ask_sidebrush_screws:
                next_step = 'tags off/double check'

            case Steps.double_check_confirmed:
                self.step = Steps.ask_tags_off

            case Steps.ask_tags_off:
                # If the notes haven't changed since we last updated CSS, we don't need to update CSS again
                if self._finish_first_copy_notes == self.text_area.text.strip():
                    next_step = 'finish track'
                else:
                    self.step = Steps.ask_copy_notes_2

            case Steps.ask_copy_notes_2:
                next_step = 'finish track'

            case Steps.wait_parts_closed:
                self.step = Steps.ask_complete_case_CSS

            case Steps.ask_complete_case_CSS:
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
                if resp.lower() in ('out', 'hold'):
                    self.phase = Phase.HOLD
                else:
                    next_step = 'order swap'

            case Steps.swap_order_S9:
                if resp.lower() in ('out', 'hold'):
                    self.phase = Phase.HOLD
                else:
                    self.step = Steps.swap_ask_refurb

            case Steps.swap_order_M6:
                if resp.lower() in ('out', 'hold'):
                    self.phase = Phase.HOLD
                else:
                    self.step = Steps.swap_ask_refurb

            case Steps.swap_order:
                if resp.lower() in ('out', 'hold'):
                    self.phase = Phase.HOLD
                else:
                    self.step = Steps.swap_move_bin

            case Steps.swap_move_bin:
                if resp.lower() == 'fb':
                    self.add_step('Freebee bin for new robot')
                elif resp.lower() == 'cx':
                    self.add_step('Moved original bin to new robot')
                elif resp.lower() == 'new':
                    self.add_step('Ordered new bin for new robot')
                elif resp:
                    return

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
                    try:
                        # '*' + at_most(2, anything) + IGNORECASE + 'swap' + at_most(8, anything) + 'bot' + optional(chunk)
                        last: re.Match = list(re.finditer(r'(?i)\*.{0,2}swap.{0,8}bot(?:.+)?', self.text_area.text))[-1]
                        t = self.text_area.text.strip()
                        self.text_area.text = t[:last.end()] + f' -> {resp} ({"" if self._is_current_swap_refurb else "non-"}refurb)' + t[last.end():]
                    except IndexError:
                        pass
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
        if self.serials:
            self.phase = Phase.DEBUGGING
        else:
            self.phase = Phase.CONFIRM
            self.step = Steps.confirm_id

    elif self.phase == Phase.UPDATING:
        self.phase = Phase.DEBUGGING


    # To simplify repeated next step logic
    if next_step == "ask pad":
        self.step = Steps.ask_came_with_pad if self.is_combo else Steps.customer_states

    if next_step == 'quiet audio':
        # TODO: abstract this into a seperate method
        if self.serial.startswith(('c', 'j')) and "evac" in self.customer_states.lower() or "empty" in self.customer_states.lower() or "app" in self.customer_states.lower():
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
        if self.can_mop:
            self.step = Steps.ask_emptied_tank
        else:
            next_step = 'screws tight'

    if next_step == 'screws tight':
        if settings.ASK_SCREWS_ON_TIGHT:
            self.step = Steps.ask_sidebrush_screws
        else:
            next_step = 'tags off/double check'

    if next_step == 'tags off/double check':
        self.step = Steps.double_check_confirmed if settings.DO_DOUBLE_CHECK else Steps.ask_tags_off

    if next_step == 'finish track':
        self.step = Steps.ask_submit_adj if self.repeat else Steps.wait_parts_closed

    if next_step == 'remove from app':
        if re.search(r'(?i)\bapp\b', self.text_area.text):
            self.step = Steps.ask_removed_provisioning
        else:
            self.step = Steps.generate_external_notes

    self.text_area.scroll_to(None, 1000, animate=False)

# All the side effects of the execute_step
# Remember to import these in Case if you add a new one!
def before_pick_up_case(self):
    clipboard.copy(self.ref)

def after_pick_up_case(self):
    self.log('open')

def after_ask_complete_case_CSS(self):
    pass
    # self.log('close')

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

def _copy_swap_serial(self):
    # This *shouldn't* happen, but just in case...
    if self.serials:
        clipboard.copy(self.serial[0].upper())

def before_swap_order(self):
    self._copy_swap_serial()

def before_swap_order_S9(self):
    self._copy_swap_serial()

def before_swap_order_M6(self):
    self._copy_swap_serial()

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
    current_date = datetime.now().strftime("%m/%d/%Y")
    minutes, seconds = divmod(self.sidebar.time, 60)
    hours, minutes = divmod(minutes, 60)
    minutes = ceil(minutes / 15) * 15
    multi_paste(
        'michelle.gonzalez@acer.com',
        f'Adjustment: {self.ref}',
        f"{self.ref}: {(str(hours) + ' hours ') if hours else ''}{minutes} minutes (finished on {current_date})"
    )
