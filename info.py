evac, visual, ir = 'evac', 'visual', 'ir'
docks = { #        is dock
    'Albany': (True, evac, visual, ir),
    'Aurora': (True, evac, visual, ir),
    'Zhuhai': (True, evac, visual),
    'Tianjin': (True, evac, ir),
    'Torino': (False, ir),
    'Fresno': (True, evac, ir),
    'San Marino': (False, ir),
    'Bombay': (False, visual),
    'Boulder': (True, evac, visual, ir),
}

EVAC_DOCKS = (
    'Albany', 'Zhuhai', 'Tianjin', 'Fresno', 'Boulder', 'Aurora'
)

DOCKS = (
    'Albany', 'Zhuhai', 'Bombay', 'Tianjin', 'Torino', 'San Marino', 'Fresno', 'Boulder', 'Aurora'
)

# TODO: move this to RobotInfo
ten_sec = 'Hold home for 10 seconds. Indicators should turn off'
lift_wheel = 'Lift one wheel and hold clean for 3 seconds. Indicators should turn off'
sleep_mode = {
    'i': ten_sec,
    's': ten_sec,
    'm': ten_sec,
    'j': lift_wheel,
    'c': lift_wheel,
    'e': 'Hold clean for 12 seconds. Release after the tone. Then, all indicators should turn off',
    'r': 'Add the plastic piece',
}

all_3 = 'Hold down all 3 buttons until the clean lights start to spin'
remove_bin = 'Remove dust bin, then hold clean for 7 seconds until it beeps. Press clean again to confirm'
factory_reset = {
    's': all_3,
    'i': all_3,
    'm': all_3,
    'j': remove_bin,
    'c': remove_bin,
    'e': 'Hold home and spot together for 20 seconds',
    'r': 'Hold dock and spot and clean until all LEDs turn on (9xx), or it beeps (6xx & 8xx)',
}


"""
irobot.support@acer.com -- michelle.gonzalez@acer.com

Make note that J5, J6 ,& J7, if it just boots (white light spins) indefinitely, then you need to replace the *battery*, with one of the following SKUs (in order of preference):
4706313
4763362
4785636
4624864
This is caused by firmware version 24.29.1

c955 -> albany
c975 -> aurora

DCT known failures:
J-Series robots with FW version 24.29.x will fail test #2 dock comms.
○ Ensure robot will evacuate and ignore DCT dock comms failure
● S9 robots may fail vacuum tests with low-current above 1000.
○ Ignore as long as value is below 1500
● Some robots will fail optical bin tests. 2 failures allowed, as long as the values are close
○ E.G. 500-1000 and the robot fails with 490.
● Pad detection tests on the M6 will sometimes fail.
○ Ignore if both wet and dry mobility missions are successful.
● C7 and C9 robots will fail actuator arm with FW's higher that 23.53.6
○ As long as the actuator arm will deploy normally during mobility and the failures
are for speed and range, ignore DCT.
● Battery charging will fail on a full battery
○ Ignore if you know the battery State of Charge is high.


Speaking of SKU's, Remember where I talked about the Costco SKU of the C9 that comes with a Zhuhai, well this is it.  If you didn't know, most C9's will come with an Aurora and the SKU is C975xxxx, but the Costco version is C955021.  As you can see, the 7 & the 5 denote the dock type.  If you get a Costco SKU, you can test it with an Albany or Zhuhai.  However, if the customer bought the Aurora separately, then you still need to test with the Aurora.  The same goes for a customer with a C7 and a stand alone Aurora purchase.


v2 J9: j955020y240911n201927
J9 v2: j955020y240911n202271

This is the optimal process for debugging being unable to provision to app, add to hints:
21386IR
Parts in: Robot, Albany, cord, lapis bin, extra filter
Claimed Damage: Minor scratches
Visible Damage: Confirmed claimed damage
Customer States: Bot won't turn on at all

Routine Checks:
* Contacts don't feel sunken
! Found signs of liquid residue
** No signs of liquid damage on the main board or connections
** No signs of liquid residue found in the user Albany
** No liquid residue found in customer bin
* No play in the blower motor, and it spins freely
* Extractors look good
* Charging contacts on the customer's Albany look good
* Tested battery: 7%/100%
* Robot charges on customer Albany @ ~22W

Process:
* Mobility test - floor, cx Albany
** Fail: undock
** Result: Fail - bot only moves one wheel, and says "wheel problem"
* Confirmed with Michelle: swapping bot, as the liquid damage is right up close to the board, if not technically on the board

* Mobility test - floor, cx Albany, new bot
** Pass: undock, dock, navigate, auto evac
** Result: Pass
* Provisioned robot to the app
* Can't provision lapis bin to robot: Keeps thinking the bin is full, tried 3 times
* Removed provisioning
* Factory reset
* Provisioned robot to the app
* RDP reset
* Unprovisioned and reprovisioned bot to app
* Tried 2 more times to provision the lapis bin
* Replacing CHM
* Still didn't work, trying a different tablet
* Swap is DOA, ordering non-referbished swap

* Mobility test - floor, cx Albany, bot #2
** Pass: undock, dock, navigate, manual evac
** Result: Pass
* Provisioned robot to the app
* Provisioned the lapis bin, and it's having the same problem, it thinks the bin is full with the lapis bin in immediately after provisioning it
* Tried a few more times
* Replacing CHM on bot #2
* Still thinking bin is full
* Reboot, on boot it gave error 15
* Factory reset
* Updated app (apparently one was available)
* Reprovisioned robot to the app
* Recognizes regular bin
* Same problem: thinks the bin is full with the lapis bin in
* Tried a test lapis bin: same thing

target window size is approx. 1103 × 988 pixels

standby voltage is 2.8V for a dock, 3.2 for a base, and once it detects a bot, it should jump up to 20, and then down to whatever the bot needs (teens). Checking the standby voltage is sufficient



All v1s
O:     J755920C230814R101633
S0:     J710020C220321N100473
S1:     J710020C210908N111709


"""
