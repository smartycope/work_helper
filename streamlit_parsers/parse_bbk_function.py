# from types import SimpleNamespace
from typing import Any

def _info(bbk:dict[str, Any]) -> dict:
    runtime_hr = bbk['RBB_CLEANING_TIME_HOURS'] + (bbk['RBB_CLEANING_TIME_MINUTES'] / 60),
    docked_hr = bbk['RBB_DOCKED_TIME_HOURS'],

    return dict(
        runtime_hr=runtime_hr,
        docked_hr=docked_hr,
        total_time_hr=docked_hr + runtime_hr,
    )

def is_value_concerning(sn, name:str, value:Any, runtime_hr=0, docked_hr=0, total_time_hr=0) -> bool:
    match name:
        case 'RBB_NUM_CHATTER':
            if value > 20:
                return True

    return False

def is_concerning(sn, bbk:dict[str, Any]) -> bool:
    """ This goes through all the BBK values and returns a dict of {value: bool} deciding whether it merits further
        inspection or not
    """
    rtn = {}
    info = _info(bbk)

    for name, value in bbk.items():
        rtn[name] = is_value_concerning(sn, name, value, **info)

    return rtn

def bbk_summary(bbk:dict[str, Any]) -> str:
    i = _info(bbk)
    return f"""\
The bot has been active for {i['total_time_hr']} ({i['runtime_hr']} hours cleaning / {i['docked_hr']} hours docked)

"""
