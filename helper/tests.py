# run with
# cd /home/zeke/hello/work_helper/
# python -m pytest . --asyncio-mode=auto

from HelperApp import HelperApp
# import HelperApp as
from Phase import Phase
from Sidebar import Sidebar
from globals import *
from Case import Case
from info import docks, factory_reset, sleep_mode
from CustomTextArea import CustomTextArea
from texts import Steps
from clipboard import paste
from textual.color import Color


colors = [
    Color.parse('#377a11'),
    Color.parse('#ef9e16'),
    Color.parse('#d1dd0b'),
    Color.parse('#ea9daf'),
    Color.parse('#799fad'),
]

SIZE = (80, 55)

async def create_case(pilot, ref='19000IR'):
    await pilot.press('n')
    await pilot.press(*ref, 'enter')
    return ref

async def test_create_new_case():
    app = HelperApp()
    async with app.run_test(size=SIZE) as pilot:
        await create_case(pilot)
        assert app.query_one("#sidebar-"+str(app.active_case.ref)).styles.background in colors

async def test_sidebar_loads():
    app = HelperApp()
    async with app.run_test(size=SIZE) as pilot:
        ref = await create_case(pilot)
        await pilot.press(*'j9j9', 'enter')

        # Just make sure the first line is good at least. Close enough.
        # print(dir(app.query_one(f'#model-label-{app.active_case.ref}')))
        assert 'J9' in app.query_one(f'#model-label-{app.active_case.ref}').renderable
        assert sleep_mode['j'][:SIDEBAR_WIDTH - 5] in app.query_one(f'#sleep-mode-label-{app.active_case.ref}').renderable
        assert factory_reset['j'][:SIDEBAR_WIDTH - 5] in app.query_one(f'#factory-reset-label-{app.active_case.ref}').renderable
        assert app.active_case.get_DCT()[:SIDEBAR_WIDTH - 5] in app.query_one(f'#dct-label-{app.active_case.ref}').renderable
        assert app.active_case.get_DCT_exceptions()[:SIDEBAR_WIDTH - 5] in app.query_one(f'#dct-exp-label-{app.active_case.ref}').renderable
        assert app.active_case.get_notes()[:SIDEBAR_WIDTH - 5] in app.query_one(f'#notes-label-{app.active_case.ref}').renderable
        assert 'J9' in app.query_one(f'#serial-label-{app.active_case.ref}').renderable
        assert ref in app.query_one(f'#ref-label-{app.active_case.ref}').renderable

# A list of lists of each current step, the text to type into the input box, and the notes it should correspond with (in order)
# The first element is the name of the test, and if it starts with "TODO", it gets skipped
# Currently, all steps in the program just add to the end of the notes, but that might not always be the case. That's why I'm leaving this here
routes = [
    [
        "TODO: Part of the most basic route",
        (Steps.confirm_id, 'j9j9', '{ref}\n'),
        (Steps.check_repeat, '', '{ref}\n'),
        (Steps.check_claimed_damage, '', '{ref}\n'),
        (Steps.pick_up_case, '', '{ref}\n'),
        (Steps.ask_dock, '', '{ref}\nParts in: Robot\n'),
        (Steps.ask_damage, '', '{ref}\nParts in: Robot\nClaimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\n'),
        (Steps.customer_states, 'bad damage', '{ref}\nParts in: Robot\nClaimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\nCustomer States: Bad damage\n\nRoutine Checks:\n'),
        (Steps.check_liquid_damage, '', '{ref}\nParts in: Robot\nClaimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\nCustomer States: Bad damage\n\nRoutine Checks:\n* No signs of liquid damage\n'),
    ],
]

async def test_routes():
    for route in routes:
        app = HelperApp()
        async with app.run_test(size=SIZE) as pilot:
            test = route.pop(0)
            if test.upper().startswith('TODO'):
                continue
            print('Testing:', test)
            ref = await create_case(pilot)
            for prompt, step, supposed_notes in route:
                assert app.active_case.step == app.active_case.input.placeholder == prompt, test
                await pilot.press(*step, 'enter')
                assert app.active_case.text_area.text == supposed_notes.format(ref=ref), test

# The exact same thing as routes, but each step assumes it adds notes to the end of the current notes (to make writing tests easier)
cumulative_routes = [
    ["Default route",
        (Steps.confirm_id, 'j9j9', '{ref}\n'),
        (Steps.check_repeat, '', ''),
        (Steps.check_claimed_damage, '', ''),
        (Steps.pick_up_case, '', ''),
        (Steps.ask_dock, '', 'Parts in: Robot\n'),
        (Steps.ask_damage, '', 'Claimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\n'),
        (Steps.customer_states, 'bad damage', 'Customer States: Bad damage\n\nRoutine Checks:\n'),
        (Steps.ask_sunken_contacts, '', '* Contacts don\'t feel sunken\n'),
        (Steps.check_liquid_damage, '', '* No signs of liquid damage\n'),
        (Steps.ask_blower_play, '', "* No play in blower motor\n"),
        (Steps.ask_cleaned, '', "* Cleaned robot\n"),
        (Steps.ask_rollers, '', ""),
        (Steps.ask_charge_test_dock, '32', "* Robot charges on test base @ ~32W\n"),
        (Steps.add_step, '', ""),
        (Steps.add_step, 'did stuff', "\nProcess:\n* Did stuff\n"),
    ],
    ["Empty id still asks for model number",
        (Steps.confirm_id, '', '{ref}\n'),
        (Steps.manual_get_serial, 'j9', ''),
        (Steps.check_repeat, '', ''),
    ],
    ["Recognizes dock",
        (Steps.confirm_id, 'j9j9', '{ref}\n'),
        (Steps.check_repeat, '', ''),
        (Steps.check_claimed_damage, '', ''),
        (Steps.pick_up_case, '', ''),
        (Steps.ask_dock, 'Zhuhai', 'Parts in: Robot, Zhuhai, cord\n'),
        (Steps.ask_damage, '', 'Claimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\n'),
        (Steps.customer_states, 'bad damage', 'Customer States: Bad damage\n\nRoutine Checks:\n'),
        (Steps.ask_sunken_contacts, '', '* Contacts don\'t feel sunken\n'),
        (Steps.check_liquid_damage, '', '* No signs of liquid damage\n'),
        (Steps.ask_blower_play, '', "* No play in blower motor\n"),
        (Steps.ask_cleaned, '', "* Cleaned robot\n"),
        (Steps.ask_rollers, '', ""),
        (Steps.ask_user_base_contacts, '', "* Charging contacts on the customer's Zhuhai look good\n"),
        (Steps.ask_charge_customer_dock, '32', "* Robot charges on customer Zhuhai @ ~32W\n"),
        (Steps.add_step, 'did stuff', "\nProcess:\n* Did stuff\n"),
    ],
    ["Damage works",
        (Steps.confirm_id, 'j9j9', '{ref}\n'),
        (Steps.check_repeat, '', ''),
        (Steps.check_claimed_damage, '', ''),
        (Steps.pick_up_case, '', ''),
        (Steps.ask_dock, 'Zhuhai', 'Parts in: Robot, Zhuhai, cord\n'),
        (Steps.ask_damage, 'Stuff is broken', 'Claimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage, stuff is broken\n'),
    ],
    ["TODO: Liquid path, without dock, with corrosion",
        (Steps.confirm_id, 'j9j9', '{ref}\n'),
        (Steps.check_repeat, '', ''),
        (Steps.check_claimed_damage, '', ''),
        (Steps.pick_up_case, '', ''),
        (Steps.ask_dock, '', 'Parts in: Robot\n'),
        (Steps.ask_damage, '', 'Claimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\n'),
        (Steps.check_liquid_damage, 'y', '! Found signs of liquid residue\n'),
        (Steps.customer_states, 'bad damage', 'Customer States: Bad damage\n\nRoutine Checks:\n'),
        (Steps.liquid_check_corrosion, 'board', '! Found signs of liquid corrosion on the board\n'),
        (Steps.liquid_check_bin, 'y', '*** Liquid residue found in customer bin: probably sucked up liquid\n'),
        # TODO: this path needs to be changed (add Process: to it)
        (Steps.liquid_take_pictures, '', '*** Liquid residue found in customer bin: probably sucked up liquid\n'),
    ],
    ["Liquid path, without dock, without corrosion",
        (Steps.confirm_id, 'j9j9', '{ref}\n'),
        (Steps.check_repeat, '', ''),
        (Steps.check_claimed_damage, '', ''),
        (Steps.pick_up_case, '', ''),
        (Steps.ask_dock, '', 'Parts in: Robot\n'),
        (Steps.ask_damage, '', 'Claimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\n'),
        (Steps.customer_states, 'bad damage', 'Customer States: Bad damage\n\nRoutine Checks:\n'),
        (Steps.ask_sunken_contacts, '', '* Contacts don\'t feel sunken\n'),
        (Steps.check_liquid_damage, 'y', '! Found signs of liquid residue\n'),
        (Steps.liquid_check_corrosion, '', '*** No signs of liquid damage on the main board or connections\n'),
        (Steps.liquid_check_bin, '', '*** No liquid residue found in customer bin\n'),
        (Steps.liquid_take_pictures, '', ''),
    ],
    ["Sunken contacts, actually good",
        (Steps.confirm_id, 'j9j9', '{ref}\n'),
        (Steps.check_repeat, '', ''),
        (Steps.check_claimed_damage, '', ''),
        (Steps.pick_up_case, '', ''),
        (Steps.ask_dock, '', 'Parts in: Robot\n'),
        (Steps.ask_damage, '', 'Claimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\n'),
        (Steps.customer_states, 'bad damage', 'Customer States: Bad damage\n\nRoutine Checks:\n'),
        (Steps.ask_sunken_contacts, 'y', ''),
        (Steps.sunken_ask_side, 'r', ''),
        # Should only accept floats
        (Steps.sunken_ask_measurement, 'j', ''),
        (Steps.sunken_ask_measurement, '3.8', '* Measured right contact: 3.8mm +/- .1\n'),
        (Steps.check_liquid_damage, '', '* No signs of liquid damage\n'),
        (Steps.ask_blower_play, '', "* No play in blower motor\n"),
    ],
    ["TODO: Sunken contacts, bad",
        (Steps.confirm_id, 'j9j9', '{ref}\n'),
        (Steps.check_repeat, '', ''),
        (Steps.check_claimed_damage, '', ''),
        (Steps.pick_up_case, '', ''),
        (Steps.ask_dock, '', 'Parts in: Robot\n'),
        (Steps.ask_damage, '', 'Claimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\n'),
        (Steps.customer_states, 'bad damage', 'Customer States: Bad damage\n\nRoutine Checks:\n'),
        (Steps.ask_sunken_contacts, 'y', ''),
        (Steps.sunken_ask_side, 'L', ''),
        # Should only accept floats
        (Steps.sunken_ask_measurement, '', ''),
        # TODO: swap robot is unfinished
        (Steps.sunken_ask_measurement, '3.79', ''),
        (Steps.check_liquid_damage, '', '* No signs of liquid damage\n'),
        (Steps.ask_blower_play, '', "* No play in blower motor\n"),
    ],
    ["Blower works",
        (Steps.confirm_id, 'j9j9', '{ref}\n'),
        (Steps.check_repeat, '', ''),
        (Steps.check_claimed_damage, '', ''),
        (Steps.pick_up_case, '', ''),
        (Steps.ask_dock, '', 'Parts in: Robot\n'),
        (Steps.ask_damage, '', 'Claimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\n'),
        (Steps.customer_states, 'bad damage', 'Customer States: Bad damage\n\nRoutine Checks:\n'),
        (Steps.ask_sunken_contacts, '', '* Contacts don\'t feel sunken\n'),
        (Steps.check_liquid_damage, '', '* No signs of liquid damage\n'),
        (Steps.ask_blower_play, 'y', "! Found play in the blower motor\n"),
        (Steps.ask_cleaned, '', "* Cleaned robot\n"),
        (Steps.ask_rollers, '', ""),
    ],
    ["Rollers works",
        (Steps.confirm_id, 'j9j9', '{ref}\n'),
        (Steps.check_repeat, '', ''),
        (Steps.check_claimed_damage, '', ''),
        (Steps.pick_up_case, '', ''),
        (Steps.ask_dock, '', 'Parts in: Robot\n'),
        (Steps.ask_damage, '', 'Claimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\n'),
        (Steps.customer_states, 'bad damage', 'Customer States: Bad damage\n\nRoutine Checks:\n'),
        (Steps.ask_sunken_contacts, '', '* Contacts don\'t feel sunken\n'),
        (Steps.check_liquid_damage, '', '* No signs of liquid damage\n'),
        (Steps.ask_blower_play, '', "* No play in blower motor\n"),
        (Steps.ask_cleaned, '', "* Cleaned robot\n"),
        (Steps.ask_rollers, 'n', "! Extractors are bad\n"),
    ],
    ["Cleaning na",
        (Steps.confirm_id, 'j9j9', '{ref}\n'),
        (Steps.check_repeat, '', ''),
        (Steps.check_claimed_damage, '', ''),
        (Steps.pick_up_case, '', ''),
        (Steps.ask_dock, '', 'Parts in: Robot\n'),
        (Steps.ask_damage, '', 'Claimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\n'),
        (Steps.customer_states, 'bad damage', 'Customer States: Bad damage\n\nRoutine Checks:\n'),
        (Steps.ask_sunken_contacts, '', '* Contacts don\'t feel sunken\n'),
        (Steps.check_liquid_damage, '', '* No signs of liquid damage\n'),
        (Steps.ask_blower_play, '', "* No play in blower motor\n"),
        (Steps.ask_cleaned, 'na', ""),
        (Steps.ask_rollers, '', ""),
        (Steps.ask_charge_test_dock, '32', "* Robot charges on test base @ ~32W\n"),
    ],
    ["Cleaning adds notes",
        (Steps.confirm_id, 'j9j9', '{ref}\n'),
        (Steps.check_repeat, '', ''),
        (Steps.check_claimed_damage, '', ''),
        (Steps.pick_up_case, '', ''),
        (Steps.ask_dock, '', 'Parts in: Robot\n'),
        (Steps.ask_damage, '', 'Claimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\n'),
        (Steps.customer_states, 'bad damage', 'Customer States: Bad damage\n\nRoutine Checks:\n'),
        (Steps.ask_sunken_contacts, '', '* Contacts don\'t feel sunken\n'),
        (Steps.check_liquid_damage, '', '* No signs of liquid damage\n'),
        (Steps.ask_blower_play, '', "* No play in blower motor\n"),
        (Steps.ask_cleaned, 'there was stuff in the thing', "* Cleaned robot - there was stuff in the thing\n"),
        (Steps.ask_rollers, '', ""),
        (Steps.ask_charge_test_dock, '32', "* Robot charges on test base @ ~32W\n"),
    ],
    ["doesn't charge",
        (Steps.confirm_id, 'j9j9', '{ref}\n'),
        (Steps.check_repeat, '', ''),
        (Steps.check_claimed_damage, '', ''),
        (Steps.pick_up_case, '', ''),
        (Steps.ask_dock, '', 'Parts in: Robot\n'),
        (Steps.ask_damage, '', 'Claimed Damage: Minor scratches\nVisible Damage: Confirmed claimed damage\n'),
        (Steps.customer_states, 'bad damage', 'Customer States: Bad damage\n\nRoutine Checks:\n'),
        (Steps.ask_sunken_contacts, '', '* Contacts don\'t feel sunken\n'),
        (Steps.check_liquid_damage, '', '* No signs of liquid damage\n'),
        (Steps.ask_blower_play, '', "* No play in blower motor\n"),
        (Steps.ask_cleaned, '', "* Cleaned robot\n"),
        (Steps.ask_rollers, '', ""),
        (Steps.ask_charge_test_dock, '32', "* Robot charges on test base @ ~32W\n"),
        (Steps.add_step, '', ""),
        (Steps.add_step, 'did stuff', "\nProcess:\n* Did stuff\n"),
    ],
]

async def test_cumulative_routes():
    for route in cumulative_routes:
        app = HelperApp()
        async with app.run_test(size=SIZE) as pilot:
            ref = await create_case(pilot)
            running_notes = ''
            test = route.pop(0)
            if test.upper().startswith('TODO'):
                continue
            print('Testing:', test)
            for prompt, step, supposed_new_notes in route:
                running_notes += supposed_new_notes.format(ref=ref)
                label = f'{test} - {prompt}: {step}'
                assert app.active_case.step == app.active_case.input.placeholder == prompt, label + ' (input box prompt test)'
                await pilot.press(*step, 'enter')
                assert app.active_case.text_area.text == running_notes, label + ' (case text test)'


async def test_copy_ref_step():
    app = HelperApp()
    async with app.run_test(size=SIZE) as pilot:
        ref = await create_case(pilot)
        await pilot.press(*'j9j9', *['enter']*3)
        assert paste() == ref


# def test_multi_paste():
#     multi_paste('a', 'b', 'c', 'd')
#     assert
