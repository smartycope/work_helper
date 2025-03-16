import json
import os
from typing import Any
import streamlit as st
# from globals import PARSE_BBK_ICON
from pathlib import Path
from parse_bbk_function import is_concerning
import pandas as pd

DEBUG = os.name != 'nt'

# st.set_page_config(layout='wide', page_title='BBK Parser', page_icon=PARSE_BBK_ICON)
BBK_LOG_DIR = Path(f"C:\\Users\\Roomba Wrangler\\Documents\\DCT\\BBK")

st.warning('This is a beta version, it may not work yet')
st.title('BBK Parser')

# C975020B240108N003454
def load_bbk(sn):
    if DEBUG:
        path = Path('example_bbk.json')
    else:
        if sn:
            path = BBK_LOG_DIR / f'BBK-{sn}.txt'
        else:
            # Find the most recently used file
            path = max(BBK_LOG_DIR.glob('*.txt'), key=os.path.getmtime)

    with path.open('r') as f:
        raw = json.load(f)['data']

    return {i['label']: i['value'] for i in raw}



user_input = st.text_input(
    label="Input the serial number",
    autocomplete='off',
    placeholder='Serial number'
)
if user_input:
    try:
        values = load_bbk(user_input)
    except Exception as err: # TODO add a specific error here
        if DEBUG:
            raise err
        else:
            st.write(':warning: Could not find that BBK log')
            st.exception(err)

    concerns = is_concerning(user_input, values)
    data = {
        'BBK': values.keys(),
        'Value': map(str, values.values()),
        'Passes': [('❌' if i else '✅') for i in concerns.values()],
        '_status': concerns.values(),
    }

    # Convert data to a DataFrame
    search = st.text_input('Search for a BBK value')
    df = pd.DataFrame(data)
    filtered_df = None

    if search:
        filtered_df = df[df["BBK"].str.contains(search, case=False, na=False)]
    else:
        if any(concerns.values()):
            filtered_df = df[df['_status']]
            # filtered_df = df.filter(df['Passes'] == '❌')
        else:
            st.write('✅ All BBK values are within spec!')

    if filtered_df is not None:
        # Display the DataFrame with a radio button for selection
        df = st.data_editor(
            filtered_df,
            column_config={
                "BBK": st.column_config.TextColumn("BBK"),
                "Value": st.column_config.TextColumn("Value"),
                "Passes": st.column_config.TextColumn("Passes"),
                '_status': None,
            },
            hide_index=True,
            # disabled=True,
        )
