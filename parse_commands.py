import re
from numpy import mean, std

from Phase import Phase
from globals import capitolize

""" Auto Acronyms:
d -> cx <dock>
r -> robot
nr -> new robot
nd -> new dock
rp -> replaced
fb -> freebee
sb -> sidebrush
doa -> DOA
exp -> expected
ACRONYM: chm -> CHM
ACRONYM: opt -> optical bin failures <100 out of range.
ACRONYM: dc -> expected dock comms failure.
ACRONYM: batt -> battery
ACRONYM: md -> module
ACRONYM: fw -> firmware
ACRONYM: sw -> software
ACRONYM: hw -> hardware
"""

ACRONYMS = {
    'fw': "firmware",
    'sw': "software",
    'hw': "hardware",
    'md': "module",
    'batt': "battery",
    'comms': "Dock comms failure.",
    'opt': "optical bin failure[s] <100 out of range.",
    'chm': "CHM",
    'exp': 'expected',
    'doa': 'DOA',
    'sb': 'sidebrush',
    'fb': 'freebee',
    'rp': 'replaced',
    'nd': 'new dock',
    'nr': 'new robot',
    'r': 'robot',
    'd': 'dock',
    'ch': 'charges on',
    'n': 'new',
    't': 'test',
    'p': 'Pass',
}

def parse_acronym(input:str):
    for acronym, full in ACRONYMS.items():
        regex = fr'(?i)\b{acronym}\b'
        input = re.sub(regex, full, input)
    return input

def parse_command(self, input:str):
    """ Parses all input from the "Add Step" step """

    args = input.strip().split(' ')
    cmd = args.pop(0).lower()

    if not cmd:
        return
# COMMAND: cleaned bot charging contacts
# COMMAND/ACRONYM: BiT: skip, non-refurb swap
    try:
        step = None
        match cmd:
            case 'b' | 'batt':
                charge = args.pop(0)
                health = args.pop(0) if args else '100'
                self.add_step(f'Battery test: {charge}%/{health}%')
            case 'fr':
                step = 'Factory reset'
            case 's' | 'sr' | 'sw':
                self.phase = Phase.SWAP
                step = 'Swap robot'
            case 'sd':
                step = 'Swap dock'
            case 'ar':
                step = 'Aurora refill debug steps'
            case 'hr':
                step = 'Hard reset'
            case 'hfr':
                step = 'Hard factory reset'
            case 'bit':
                notes = args.pop(0) if args else 'pass'
                step = f'BiT: {notes}'
            case 'bbk':
                notes = args.pop(0) if args else 'pass'
                step = f'BBK: {notes}'
            case 'ms' | 'meas':
                if not args:
                    self.add_step('Measured both contacts: >4mm')
                else:
                    side = args.pop(0)
                    # This is copied from step_algorithm
                    # TODO: abstract this into a method
                    measurements = list(map(float, args))
                    meas = mean(measurements)
                    meas = round(meas, 1 if 3.8 > meas > 3.74 else 2)
                    self.add_step(f'Measured {"right" if side.lower() == "r" else "left"} contact: {meas}mm +/- {max(std(measurements), .1):.1f}')
            # TODO: I need a better way to do this
            # case 'ch' | 'charge':
                # watts = args.pop(0)
                # dock = args.pop(0) if args else 'dock'
                # bot = args.pop(0) if args else 'Robot'
                # step = f'{bot} charges on {dock} @ ~{watts}W'
            case 'blew' | 'chirp':
                step = 'Blew out chirp sensors'
            case 'diag':
                step = 'Diagnosis:'
                args[0] = capitolize(args[0])
            case 'cdc' | 'cln':
                if args:
                    if args[0].lower() == 'b':
                        args.pop(0)
                    step = 'Cleaned bot charging contacts'
                else:
                    step = 'Cleaned dock charging contacts'
            case 'prov':
                if not args:
                    step = 'Provisioned robot to the app'
                else:
                    match args.pop(0):
                        case 'app': step = 'Provisioned robot to the app'
                        case 'lapis': step = 'Provisioned lapis bin on app'
                        # Don't allow notes here, where would they go?
                        case 'both':
                            self.add_step('Provisioned robot to the app')
                            self.add_step('Provisioned lapis bin on app')
            case 'reprov':
                step = 'Reprovisioned robot to the app'
            case 'fb':
                step = 'Freebee'
            case '2m':
                step = 'Double checked with Michelle'
            case 'cm':
                step = 'Confirmed with Michelle'
            case 'rm':
                step = 'Removed provisioning'
            case 'rp':
                step = 'Replaced'
            case 'bump':
                side = args.pop(0) if args else 'inside and out'
                step = f'Cleaned {side}side of the bumper'
            case 'am':
                step = 'Attempted mobility test:'

            # COMMAND: ch doc is wrong - also ch just sucks, I need a new way to do it ("new Torino" has a space in it)

            case _:
                raise
        if step:
            self.add_step(step + ' ' + parse_acronym(' '.join(args)))
    except:
        self.add_step(capitolize(parse_acronym(input)).strip())
