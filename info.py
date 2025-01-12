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
lift_wheel = 'Lift one wheel and hold clean for 3 seconds. Indicators should turn off, then press clean again to confirm'
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
