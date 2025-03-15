# from types import SimpleNamespace
from typing import Any

def is_value_concerning(sn, name:str, value:Any, runtime_hr=0, docked_hr=0, total_time_hr=0) -> bool:
    match name:
        case 'RBB_NUM_CHATTER':
            if value > 20:
                return True

    return False
