import streamlit as st

try:

    import json
    import os
    from typing import Any
    # from globals import PARSE_BBK_ICON
    from pathlib import Path
    from parse_bbk_function import is_concerning
    import pandas as pd
    from globals.RobotInfo import RobotInfo
    from st_keyup import st_keyup

    ss = st.session_state

    # DEBUG = os.name != 'nt'
    DEBUG = False

    # st.set_page_config(layout='wide', page_title='BBK Parser', page_icon=PARSE_BBK_ICON)
    BBK_LOG_DIR = Path("C:\\Users\\Roomba Wrangler\\Documents\\DCT\\BBK")

    st.warning('This is a beta version, it may not work yet')
    st.title('BBK Parser')

    # C975020B240108N000000
    def load_bbk(file):
        # BBK-J755020Y240402N100000.txt
        return file.name[4:-4], {i['label']: i['value'] for i in json.load(file)['data']}


    ss['file'] = st.file_uploader('Uploade BBK file', 'txt', False, help='Upload the BBK data in DCT, and then press this button, and upload the most recent file in "C:\\Users\\Roomba Wrangler\\Documents\\DCT\\BBK". Make sure the "export data to file" checkbox is selected')
    if ss.get('file'):
        try:
            sn, values = load_bbk(ss.get('file'))
            st.write(sn)
        except Exception as err: # TODO add a specific error here
            if DEBUG:
                raise err
            else:
                st.write(":warning: Could not locate the BBK log :warning:\n\nMake sure you're running this on a wrangler.\n\nIt gave this error:")
                st.exception(err)
        else:
            # ss['info'] = RobotInfo(sn)
            ss['info'] = RobotInfo()
            ss['info'].add_serial(sn)
            ss['bbk'] = values

    if ss.get('info') and ss.get('bbk'):
        concerns = is_concerning(ss['info'], ss['bbk'])
        data = {
            'BBK': ss['bbk'].keys(),
            'Value': map(str, ss['bbk'].values()),
            'Passes': [('❌' if i else '✅') for i in concerns.values()],
            '_status': concerns.values(),
        }

        # Convert data to a DataFrame
        # search = st.text_input('Search for a BBK value')
        search = st_keyup('Search for a BBK value')

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

except Exception as err:
    st.exception(err)
