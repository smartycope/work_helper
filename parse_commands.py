from numpy import mean, std

def parse_command(self, input:str):
    args = input.strip().split(' ')
    cmd = args.pop(0).lower()

    if not cmd:
        return

    try:
        step = None
        match cmd:
            case 'b' | 'batt':
                charge = args.pop(0)
                health = args.pop(0) if args else '100'
                self.add_step(f'Battery test: {charge}%/{health}%')
            case 'fr':
                step = 'Factory reset'
            case 's' | 'sr':
                step = 'Swapped robot'
            case 'sd':
                step = 'Swapped dock'
            # case 'ch' | 'charg' | 'charge':
            #     step = ''
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
            case 'ch' | 'charge':
                watts = args.pop(0)
                dock = args.pop(0) if args else 'dock'
                bot = args.pop(0) if args else 'Robot'
                step = f'{bot} charges on {dock} @ ~{watts}W'
            case 'blew' | 'chirp':
                step = 'Blew out chirp sensors'
            case 'diag':
                step = 'Diagnosis: '
            case 'cdc' | 'cln':
                step = 'Cleaned dock charging contacts'
            case 'prov':
                step = 'Provisioned robot to the app'
            case _:
                raise
        if step:
            self.add_step(step + ' ' + ' '.join(args))
    except:
        r = input.strip()
        self.add_step(r[0].upper() + r[1:])
