import streamlit as st

from work_helper.globals.RobotInfo import RobotInfo

EXPLANATION = """\
Enter a model number, a serial number, or 2 serial numbers back to back. If 2 serial numbers are given,
it will confirm that they're the same, and warn you if they're not. For example, All of these inputs will work:

i8

i8557

i855720C230814R100000

i855720C230814R100000i855920C230814R100000
"""

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
            st.write(f"### ⚠️ Serial numbers are different! ⚠️\n{ids[half:]}\n\n{ids[:half]}")
            info = None
        else:
            info.add_serial(ids[half:])

if info:
    info: RobotInfo
    if info.has_weird_i5g:
        st.warning(' Possibly a factory provisioned lapis bin', icon='⚠️')
    if info.serial.startswith('c9'):
        st.warning("Remember to remove battery before removing the CHM", icon='⚠️')
    if info.is_factory_lapis:
        st.error('Factory provisioned lapis bin!', icon='⚠️')

    platform = info.get_platform()

    f":blue[{info.get_quick_model()} {('• ' + platform) if platform else ''}]"

    if len(info.serial) > 3:
        f":gray[{info.serial.upper()}]"

    f"""
DCT: {info.get_DCT(streamlit=True)}

### DCT Exceptions
{info.get_DCT_exceptions()}

### Shipping Mode
{info.sleep_mode.get(info.serial[0], 'Unknown')}

### Factory Reset
{info.factory_reset.get(info.serial[0], 'Unknown')}

### Notes
{info.get_notes(False)}
"""
