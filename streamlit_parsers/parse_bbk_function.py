# from types import SimpleNamespace
from collections import Counter
from typing import Any
import streamlit as st
from work_helper.globals import RobotInfo


def is_concerning(info:RobotInfo, bbk:dict[str, Any]) -> bool:
    """ This goes through all the BBK values and returns a dict of {value: bool} deciding whether it merits further
        inspection or not
    """
    try:
        runtime_hr = bbk['RBB_CLEANING_TIME_HOURS'] + (bbk['RBB_CLEANING_TIME_MINUTES'] / 60),
        docked_hr = bbk['RBB_DOCKED_TIME_HOURS'],
        total_time_hr=docked_hr + runtime_hr
        missions_started = bbk['RBB_NUM_MISSIONS_STARTED']
        missions_failed = bbk['RBB_NUM_MISSIONS_FAILED']
        missions_canceled = bbk['RBB_NUM_MISSIONS_CANCELED']
        missions_completed = bbk['RBB_NUM_MISSIONS_COMPLETED']
        pause_ids = {f'RBB_LAST_PAUSE_IDS_{i}': bbk[f'RBB_LAST_PAUSE_IDS_{i}'] for i in range(1, 11)}

        rtn = {}

        # Check any plain values being out of threshold
        for name, value in bbk.items():
            rtn[name] = (
                (name == 'RBB_NUM_CONSTANT_BUMP' and (value > 150 or (value > 10 and info.i_series))) or
                (name == 'RBB_NUM_FAILED_CHARGES' and value > 40) or
                (name == 'RBB_NUM_WHEEL_DROPS' and value > 7_000) or
                # If we're getting stuck more than 3 times per mission
                (name == 'RBB_NUM_STUCKS' and (value / missions_started > 3 or value > 10_000))
            )

        # Some more checks
        if missions_failed / missions_started > .5:
            rtn['RBB_NUM_MISSIONS_FAILED'] = True

        # Check all the pause IDs
        pauses = Counter(pause_ids.values()).most_common()
        concern_pauses = []
        for id, cnt in pauses:
            id = id.lower()
            if (
                ('batt' not in id and cnt >= 4) or
                ('26' in id and info.S9 and cnt > 1) or # blower stall
                ('bumper' in id and cnt >= 4) or
                ('68' in id and cnt >= 3) or
                ('no bump' in id and cnt >= 3) or # R series error
                ('charg' in id and 'current' in id and cnt >= 3)
            ):
                concern_pauses.append(id)

        for id, val in pause_ids.items():
            if val in concern_pauses:
                rtn[id] = True

    except KeyError as err:
        st.exception(err)
        return {name: False for name in bbk.keys()}

    return rtn

def bbk_summary(bbk:dict[str, Any]) -> str:
    runtime_hr = bbk['RBB_CLEANING_TIME_HOURS'] + (bbk['RBB_CLEANING_TIME_MINUTES'] / 60),
    docked_hr = bbk['RBB_DOCKED_TIME_HOURS'],
    total_time_hr=docked_hr + runtime_hr

    return f"""\
The bot has been active for {total_time_hr} ({runtime_hr} hours cleaning / {docked_hr} hours docked)
"""
