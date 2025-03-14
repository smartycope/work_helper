import streamlit as st

from globals import PARSE_BBK_ICON, SERIAL_PARSER_ICON

pg = st.navigation([
    st.Page('serial_parser_streamlit.py', title='Serial Parser', icon=SERIAL_PARSER_ICON),
    st.Page('parse_bbk.py', title='BBK Parser', icon=PARSE_BBK_ICON),
])
pg.run()
