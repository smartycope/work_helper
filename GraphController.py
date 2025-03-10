from abc import ABC
from typing import Callable, Iterable
import dis
import graphviz

class State:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.transition = None
        self._simple = None

    def __rshift__(self, other):
        if isinstance(other, State):
            self._simple = other
            self.transition = lambda *args, **kwargs: other
        elif callable(other):
            self._simple = False
            self.transition = other
        else:
            raise ValueError('Invalid transition')

        return self, self.transition

    def __eq__(self, other):
        if isinstance(other, State):
            return self.value == other.value and self.name == other.name
        elif isinstance(other, str):
            return self.value == other
        else:
            return False

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f'<State {self.name}>'

class States:
    def __init_subclass__(cls):
        cls._states = {name: State(name, value) for name, value in cls.__dict__.items() if not name.startswith('_')}
        """ A dict of all states, with the name as the key and the State instance as the value """

        cls._states_lookup = {value: State(name, value) for name, value in cls.__dict__.items() if not name.startswith('_')}
        """ A dict of all states, with the State instance as the key and the name as the value """

        cls._states_list = list(cls._states.values())
        """ A list of all states, in the order they were defined """

        for name, value in cls._states.items():
            setattr(cls, name, State(name, value))

# TODO: duplicate states should be detected and disallowed
class GraphController:
    initial:State = None
    states:States = None
    transitions:Iterable[Callable] = []

    def __init__(self):
        assert self.initial is not None, 'Initial state must be set'
        assert self.states is not None, 'States must be set'
        assert self.transitions is not None, 'Transitions must be set'

        self._state = None
        self.state = self.initial
        self._transitions:dict[State, Callable] = {s: t for s, t in self.transitions}

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        old = self._state
        new = value

        assert isinstance(new, State), 'Invalid state'
        assert new in self.states._states_list, 'Invalid state'

        # If we have a method named `after_<step_name>`, then call it
        if old is not None:
            method_name = 'after_' + old.name
            if hasattr(self, method_name):
                getattr(self, method_name)()

        method_name = 'before_' + new.name
        if hasattr(self, method_name):
            getattr(self, method_name)()

        self._state = value

    def __next__(self):
        self.next()

    def next(self, *args, **kwargs):
        # Apparently adding self like this works
        self.state = self._transitions[self.state](self, *args, **kwargs)
        # Keep calling the returned function until it returns a state
        while not isinstance(self.state, State):
            try:
                self.state = self.state(self, *args, **kwargs)
            except TypeError as err:
                raise TypeError(f'Invalid return type from {self.state}: all transition methods should return a function or a State') from err


    # This would probably be easier and work better if it used ast instead of dis
    @staticmethod
    def get_returns(func):
        # return [instr.argrepr for instr in dis.Bytecode(func) if instr.opname in ("RETURN_CONST", "RETURN_VALUE")]
        rtn = []
        stack = []  # Tracks last loaded values

        for instr in dis.Bytecode(func):
            if instr.opname in {"LOAD_FAST", "LOAD_GLOBAL", "LOAD_DEREF", "LOAD_CONST", 'LOAD_ATTR'}:  # Variable names
                stack.append(instr.argval)
            elif instr.opname == "RETURN_VALUE":
                if stack:  # Use last loaded value (var name or literal)
                    rtn.append(stack[-1])
            elif instr.opname == "RETURN_CONST":
                rtn.append(instr.argval)

        return rtn

    def construct_graphvis(self, use_names=True):
        dot = graphviz.Digraph(comment='State Machine')

        def add_function_outputs(trans):
            for ret in self.get_returns(trans):
                if ret in [i.name for i in self.states._states_list]:
                    state = self.states._states[ret]
                    dot.edge(trans.__name__, state.name if use_names else state.value)
                # It's a function
                elif hasattr(self, ret):
                    dot.edge(trans.__name__, ret)
                    add_function_outputs(getattr(self, ret))
                else:
                    raise ValueError(f'return value is not a state nor a method in self. Got {ret!r}')

        # Add states as nodes
        for state, transition in self._transitions.items():
            state: State
            transition: Callable

            # No idea why it's state.value.value here, instead of state.value
            label = state.name if use_names else state.value.value

            # dot.node(state.name, label, shape='circle')
            dot.node(state.name, label, shape='box')
            if state._simple:
                dot.edge(state.name, state._simple.name)
            # If it's not simple, then it's a function
            else:
                dot.node(transition.__name__, transition.__name__, shape='circle')
                dot.edge(state.name, transition.__name__)

                add_function_outputs(transition)

        return dot


class TestStates(States):
    a = 'this is a'
    b = 'this is b'
    c = 'this is c'

class TestGraph(GraphController):
    def do_the_thing(self, decider=True):
        print('Deciding...')
        print('\tself=', self)
        print('\tdecider=', decider)
        if decider:
            print('decided on a')
            return TestStates.a
        else:
            print('decided on c')
            return TestStates.c

    def before_a(self):
        print('Before a')

    def after_a(self):
        pass
        # print('After a')

    def before_b(self):
        print('Before b')

    def before_c(self):
        print('Before c')

    def after_c(self):
        pass
        # print('After c')

    states = TestStates
    initial = TestStates.a
    transitions = (
        TestStates.a >> TestStates.b,
        TestStates.b >> do_the_thing,
        TestStates.c >> TestStates.a
    )
