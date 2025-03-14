import streamlit as st

from RobotInfo import RobotInfo
# from ExternalNotesMenu import ExternalNotesMenu
# from HintsMenu import HintsMenu
from globals import PASSWORD, SERIAL_PARSER_ICON

st.set_page_config(layout='wide', page_title='Serial Parser', page_icon=SERIAL_PARSER_ICON)

EXPLANATION = """\
Enter a model number, a serial number, or 2 serial numbers back to back. If 2 serial numbers are given,
it will confirm that they're the same, and warn you if they're not. For example, All of these inputs will work:

i8

i8557

i855720C230814R100000

i855720C230814R100000i855920C230814R100000
"""

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Password authentication
if not st.session_state["authenticated"]:
    given_password = st.text_input("Enter password", key="password_input", type="password")
    if given_password == PASSWORD:
        st.session_state["authenticated"] = True
        st.rerun()
    elif given_password:
        st.write("Incorrect password. Please try again.")
        st.stop()
    else:
        st.stop()

# Main application UI
st.title("Serial Parser")

info = None
user_input = st.text_input(
    label="Input the model, or 1 or 2 serial numbers",
    help=EXPLANATION,
    autocomplete='off',
    placeholder='Serial number'
)
if user_input:
    info = RobotInfo()
    ids = user_input.lower()
    if len(ids) % 2 or len(ids) <= 25:
        info.add_serial(ids)
    else:
        half = len(ids) // 2
        if not info._ids_equal(ids[half:], ids[:half]):
            st.write(f"### ⚠️ Serial numbers are different! ⚠️\n{ids[half:]}\n{ids[:half]}")
        else:
            info.add_serial(ids[half:])

if info:
    st.write(info.statement_st())
