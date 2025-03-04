import re
from numpy import mean, std

from Phase import Phase
from globals import capitolize
import settings

ACRONYMS = {
    # sprayer off current of n.
    'wh': 'wheel',
    'whs': 'wheels',
    'nm': 'non-modular',
    'br': 'broken',
    'ds': 'docks',
    'dg': 'docking',
    'i': 'I',
    'err': 'error',
    'errs': 'errors',
    'ir': 'IR',
    'r': 'robot',
    'lq': 'liquid',
    'ls': 'liquid spill',
    'btn': 'button',
    'btns': 'buttons',
    'diag': 'Diagnosis',
    'mt': 'mobility test',
    'mts': 'mobility tests',
    'ml': 'manual',
    'ev': 'evac',
    'evs': 'evacs',
    'ss': 'smart scrub',
    'dd': 'dirt detect',
    'b': 'robot',
    'd': 'dock',
    'n': 'new',
    'l': 'lapis bin',
    't': 'test',
    'p': 'Pass',
    'vc': 'vacuum',
    'fl': 'filter',
    'ft': 'filter',
    'ex': 'extractors',
    'od': 'ordered',
    'fw': "firmware",
    'sw': "software",
    'hw': "hardware",
    'md': "module",
    'bt': "battery",
    'sn': 'serial number',
    'oem': 'OEM',
    'chm': "CHM",
    'bbk': 'BBK',
    'doa': 'DOA',
    'dct': 'DCT',
    'rdp': 'RDP',
    'rcon': 'RCON',
    'bb': 'false bump',
    'exp': 'expected',
    'sb': 'sidebrush',
    'fb': 'freebee',
    'rp': 'replaced',
    'nd': 'new dock',
    'nr': 'new robot',
    'ch': 'charge',
    'chg': 'charging',
    'chd': 'charged',
    'chs': 'charges',
    'cho': 'charges on',
    'cm': 'Confirmed with Michelle',
    'ar': 'Aurora refill debug steps',
    'fr': 'factory reset',
    'hr': 'hard reset',
    # 'bit skip': 'skip, non-refurb swap',
    'hfr': 'hard factory reset',
    'lowvac': 'Low current vacuum test <1500.',
    'comm': "Dock comms failure.",
    'batt full': "Battery current test failed (full battery).",
    'opt': "optical bin failure[s] <100 out of range.",
    'opt150': "optical bin failure[s] <150 out of range.",
    'opt100': "optical bin failure[s] <100 out of range.",
    'opt50': "optical bin failure[s] <50 out of range.",
    'opt20': "optical bin failure[s] <20 out of range.",
    'pad act': "pad actuator deploy/stow failure[s].",
}

def parse_acronym(input:str):
    for acronym, full in ACRONYMS.items():
        # if_not_preceded_by(any_of(*r"'-_")) + wordBoundary + 'ttt' + wordBoundary + IGNORECASE
        regex = fr"(?i)(?<!(?:'|\-|_))\b{acronym}\b"
        input = re.sub(regex, full, input)
    return input

def parse_command(self, input:str):
    """ Parses all input from the "Add Step" step """

    args = input.strip().split(' ')
    cmd = args.pop(0).lower()

    if not cmd:
        return

    try:
        step = None
        match cmd:
            case 'batt':
                charge = args.pop(0)
                health = args.pop(0) if args else '100'
                self.add_step(f'Battery test: {charge}%/{health}%')
            case 's' | 'sr' | 'sw':
                self.phase = Phase.SWAP
                step = 'Swap robot'
            case 'sd':
                step = 'Swap dock'
            case 'bit':
                step = 'BiT:'

                if args and args[0].lower() == 'skip':
                    args.pop(0)
                    step += ' skipping, non-refurb swap'

                if not args:
                    step += ' Pass'
            case 'bbk':
                notes = args.pop(0) if args else 'pass'
                step = f'BBK: {notes}'
            case 'meas':
                side = args.pop(0).lower()
                if not args:
                    # self.add_step('Measured both contacts: >4mm')
                    if side == 'b':
                        self.add_step('Measured both contacts: >4mm')
                    else:
                        self.add_step(f'Measured {"right" if side.lower() == "r" else "left"} contact: >4mm')
                else:
                    measurements = list(map(float, args))
                    self.add_measure_contacts_step(side, measurements)
            case 'blew':
                if args:
                    which = args.pop(0).lower()
                    if which == 'cliff':
                        step = 'Blew out cliff sensors'
                    elif which == 'chirp':
                        step = 'Blew out chirp sensors'
                else:
                    step = 'Blew out chirp sensors'
            case 'cln':
                if args:
                    if args[0].lower() in ('b', 'r'):
                        args.pop(0)
                    step = 'Cleaned bot charging contacts'
                else:
                    step = 'Cleaned dock charging contacts'
            case 'prov':
                if not args:
                    step = 'Provisioned robot to the app'
                else:
                    match args.pop(0):
                        case 'app'|'a': step = 'Provisioned robot to the app'
                        case 'lapis'|'l': step = 'Provisioned lapis bin on app'
                        # Don't allow notes here, where would they go?
                        case 'both'|'b':
                            self.add_step('Provisioned robot to the app')
                            self.add_step('Provisioned lapis bin on app')
            case 'reprov':
                step = 'Reprovisioned robot to the app'
            case 'rm':
                step = 'Removed provisioning'
            case 'bump':
                side = args.pop(0) if args else 'inside and out'
                step = f'Cleaned {side}side of the bumper'
            case 'am':
                step = 'Attempted mobility test:'
            case 'upfw':
                step = 'Update firmware'
            case 'nozzle':
                step = 'Cleaned out drip nozzles'
            # COMMAND: ch doc is wrong - also ch just sucks, I need a new way to do it ("new Torino" has a space in it)

            case _:
                raise
        if step:
            result = step + ' ' + parse_acronym(' '.join(args))
            self.add_step(result)
            if 'BiT' in result and 'pass' in result.lower() and settings.FINISH_AFTER_SUCCESSFULL_BIT:
                self.phase = Phase.FINISH
    except:
        self.add_step(capitolize(parse_acronym(input)).strip())
