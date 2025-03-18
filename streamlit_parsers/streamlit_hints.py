import json
import streamlit as st
from pathlib import Path

with (Path(__file__).resolve().parent / '..' / 'data' / 'hints.json').open() as f:
    hints = json.load(f)

for problem, solutions in hints.items():
    with st.expander(problem):
        st.markdown('* ' + '\n* '.join(solutions))
        # for solution in solutions:
            # st.markdown(sost.write(solution)
