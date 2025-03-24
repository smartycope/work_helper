import streamlit as st
from streamlit.components.v1 import html
from DynamicStateMachine.DynamicStateMachine import DynamicStateMachine, States


class ExampleStates(States):
    a = 'this is a'
    b = 'this is b'
    c = 'this is c'
    # A virtual State
    pre_c = '5'


class ExampleMachine(DynamicStateMachine):
    def do_the_thing(self, decider=True):
        # Transition methods can have side effects
        # print('Deciding...')

        if decider:
            # print('Decided on a')
            return ExampleStates.a, 'if decider is True'
        else:
            # print('Decided on c')
            return ExampleStates.pre_c

    def decide_if_done(self, done=False):
        # print('Deciding if done...')
        if done:
            # print('Decided we\'re done')
            return None, 'Im done talking to you now.'
        else:
            # print('Decided we\'re not done')
            return ExampleStates.a, 'no keep going!'

    states = ExampleStates
    initial = ExampleStates.a
    transitions = (
        # Can be either simple transitions, like so
        ExampleStates.a >> ExampleStates.b,
        # ...or transition methods that determine the next state
        ExampleStates.b >> do_the_thing,
        ExampleStates.pre_c >> ExampleStates.c,
        # Transition methods can return a state, another transition method, or None
        ExampleStates.c >> decide_if_done,
    )


class ExampleStreamlitMachine(ExampleMachine):
    def next(self, resp, *args, **kwargs):
        if resp == '<empty>':
            resp = ''

        rtn = super().next(resp, *args, **kwargs)
        return rtn

# Add some JavaScript to hack a couple things
    # This ensures that focus stays on the text box on every rerun
    # It lets the text box accept an empty string as input (it technically gets converted to "<empty>", which gets set to an
    #     empty string later in the script)

    # This assumes there is only 1 text input box, and that there exists a button with the text "next" in it, which is triggered
    #     when Enter is pressed in the input box when it is empty
# I think this is here just so it forces the html widget to reupdate every rerun. Not sure why it needs to do that though.
if 'counter' not in st.session_state:
    st.session_state['counter'] = 0
st.session_state['counter'] += 1
html(f"""
    <p>{st.session_state['counter']}</p>
    <script>
        var input = window.parent.document.querySelectorAll("input[type=text]");
        var button = window.parent.document.querySelectorAll("button");

        for (var i = 0; i < input.length; ++i) {{
            input[i].focus();
            input[i].addEventListener("keydown", function(event) {{
                if (event.key === "Enter" && event.srcElement.value === '') {{
                    event.srcElement.value = '<empty>';
                    for (var j = 0; j < button.length; ++j) {{
                        if (button[j].innerText === 'next'){{
                            button[j].click();
                            break;
                        }}
                    }}
                }}
            }});
        }}
    </script>
    """,
    height=0,
)

# Initialize the State Machine
if 'machine' not in st.session_state:
    st.session_state['machine'] = ExampleStreamlitMachine()

# Ensure resp exists
if 'resp' not in st.session_state:
    st.session_state['resp'] = ''

resp = st.session_state['resp']
old_state = st.session_state['machine'].state

# If the State Machine is finished
if st.session_state['machine'].state is None:
    st.text('All done!')
    st.stop()


input_col, button_col = st.columns(2)

# Don't know why this works, but it kinda does
button_col.text(''); button_col.text('')
button_col.button('next')

input_col.text_input(
    label=st.session_state['machine'].state.value,
    placeholder=st.session_state['machine'].state.value,
    autocomplete='off',
    # label_visibility='hidden',
    key='resp',
)

# It SHOULD be returned, I don't know why it's not
st.session_state['machine'].next(resp)
new_state = st.session_state['machine'].state

st.write(f'Response was: {resp}')
st.write(f'Previous State was: {old_state}')
st.write(f'New state is: {new_state}')
