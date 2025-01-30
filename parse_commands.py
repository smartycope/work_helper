import re

def parse_command(self, input:str):
    args = input.strip().split(' ')
    cmd = args.pop(0).lower()

    if not cmd:
        return

    try:
        match cmd:
            case 'b' | 'batt':
                self.add_step(f'Battery test: {args[0]}%/{args[1] if len(args) > 1 else 100}%')
            case 'fr':
                self.add_step('Factory reset')
            case 's' | 'sr':
                self.add_step('Swapped robot')
            case 'sd':
                self.add_step('Swapped dock')
            # case 'ch' | 'charg' | 'charge':
            #     self.add_step('')
            case 'ar':
                self.add_step('Aurora refill debug steps')
            case _:
                raise
    except:
        r = input.strip()
        self.add_step(r[0].upper() + r[1:])
