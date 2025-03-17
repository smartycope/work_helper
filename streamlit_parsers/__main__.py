import streamlit as st
import sys, os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from globals import PARSE_BBK_ICON, SERIAL_PARSER_ICON

st.set_page_config(layout='wide', page_title='iRobot Parsers', page_icon='🤖')

pg = st.navigation([
    st.Page('serial_parser_streamlit.py', title='Serial Parser', icon=SERIAL_PARSER_ICON),
    st.Page('parse_bbk.py', title='BBK Parser', icon=PARSE_BBK_ICON),
])

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Password authentication
if not st.session_state["authenticated"]:
    given_password = st.text_input("Enter password", key="password_input", type="password")
    if given_password == st.secrets['PASSWORD']:
        st.session_state["authenticated"] = True
        st.rerun()
    elif given_password:
        st.write("Incorrect password. Please try again.")
else:
    pg.run()
