evac, visual, ir = 'evac', 'visual', 'ir'
docks = { #        is dock
    'Albany': (True, evac, visual, ir),
    'Aurora': (True, evac, visual, ir),
    'Bombay': (False, visual),
    'Boulder': (True, evac, visual, ir),
    'Fresno': (True, evac, ir),
    'San Marino': (False, ir),
    'Tianjin': (True, evac, ir),
    'Torino': (False, ir),
    'Zhuhai': (True, evac, visual),
}

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

spot_and_clean = 'Hold down all 3 buttons until the clean lights start to spin'
remove_bin = 'Remove dust bin, then hold clean for 7 seconds until it beeps. Press clean again to confirm'
factory_reset = {
    's': spot_and_clean,
    'i': spot_and_clean,
    'j': remove_bin,
    'c': remove_bin,
    'e': 'Hold home and spot together for 20 seconds',
    'r': 'Hold dock and spot and clean until all LEDs turn on (9xx), or it beeps (6xx & 8xx)',
    'm': 'Go ask',
}


"""
irobot.support@acer.com -- michelle.gonzalez@acer.com

Make note that J5, J6 ,& J7, if it just boots (white light spins) indefinitely, then you need to replace the *battery*, with one of the following SKUs (in order of preference):
4706313
4763362
4785636
4624864
This is caused by firmware version 24.29.1


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
"""
