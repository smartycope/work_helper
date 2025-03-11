from abc import ABC
import inspect
from typing import Any, Callable, Iterable, Literal, LiteralString
import dis, ast
import graphviz

# TODO: make this it's own project, with a repo and a package. It's too good to stay here

class State:
    """ A state in our state machine. It holds a name, a value, and a transition, and can be connected
    to other states via the `>>` operator.
    """

    def __init__(self, name:str, value:Any, virtual=False):
        self.name = name
        """ The variable name of the state when it was defined """
        self.value = value
        """ The value of the state when it was defined. Intentionally untyped. """
        self.transition:Callable = None
        """ The transition function to the next state. Gets called to determine the state after this one. """
        self.virtual = virtual
        """ A virtual state is one that immediately transitions to the next state without requiring a call to `next()`. """
        self._simple = None
        """ A state is simple if it only transitions to a single state. """

    def __rshift__(self, other):
        """ If the right hand side is a State, then it's a simple transition, and self.transition
        gets set to a lambda that returns the given state.
        If it's a method then it will be called to determine the next state.
        NOTE: `other` must be a method of the GraphController subclass! It cannot be a standalone function.
        (at least for now)
        """
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
    """ An abstract class that must be subclassed to define states. It will automatically create State instances
    for each class variable defined in the subclass. If a variable is set to None, then it will be considered a
    "virtual state", and will immediately transition to the next state without requiring a call to `next()`.
    In the future, instancing States directly will be supported, but it's not yet.
    """

    def __init_subclass__(cls):
        cls._states = {}
        """ A dict of all states, with the name as the key and the State instance as the value """
        cls._states_lookup = {}
        """ A dict of all states, with the State instance as the key and the name as the value """
        cls._states_list = []
        """ A list of all states, in the order they were defined """

        for name, value in cls.__dict__.items():
            if not name.startswith('_'):
                state = State(name, value, virtual=value is None)
                cls._states[name] = state
                cls._states_lookup[value] = state
                cls._states_list.append(state)
                setattr(cls, name, state)

        # cls._states = {name: State(name, value) for name, value in cls.__dict__.items() if not name.startswith('_')}
        # cls._states_lookup = {value: State(name, value) for name, value in cls.__dict__.items() if not name.startswith('_')}
        # cls._states_list = list(cls._states.values())

        # for name, value in cls._states.items():
        #     setattr(cls, name, State(name, value))

class DynamicStateMachine:
    """ A state machine that has dynamic transitions between states. It requires an initial state, a
    reference to the States subclass, and a list of transitions. Transitions can be either a simple
    state transition (one state to the next), or a method that will be called to determine the next
    state.
    Methods in this class used as transitions must return one of the following:
        - A member of the States subclass
        - Another transition method of this class that follows the same rules
        - None, to indicate the end of the state machine

    Rules for transitions:
        - Each state should only be on the left hand side (be transitioned from) once (enforced, but not warned)
        - Methods on the right hand side must be methods of this class's subclass, and not standalone functions (this is enforced at the moment)
        - Infinite loops function, and may be intentional, and thus are not checked for
        - Infinite virtual loops (a cycle of all virtual States) will result in a max recursion error. This is not checked for explicitly
    """

    def __init__(self,
        states:type[States],
        initial:State,
        transitions:Iterable[tuple[State, Callable]],
        start_immediately=True,
        trigger_initial_side_effects=True
    ):
        """
        `initial`:
                The initial state of the state machine
        `states`:
                The States subclass that defines the states as class variables
        `transitions`:
            A list of transitions. Each transition is defined by using the >> operator on two states or a
            state and a method. The method must be a method of this class's subclass, and not a standalone
            function.
        """
        self.initial = initial
        """ The initial state of the state machine """
        self.states = states
        """ The States subclass that defines the states as class variables"""
        self._trigger_initial_side_effects = trigger_initial_side_effects
        """ If True, then the initial state's before_<state> method will be called on instantiation. """

        self._state = None

        # Convert the transitions into a dict for faster lookup, ease of internal use, and ensuring uniqueness
        self._transitions:dict[State, Callable] = {s: t for s, t in transitions}

        if start_immediately:
            self.start()

    def start(self):
        """ Start the state machine. """
        self.on_start()
        if self._trigger_initial_side_effects:
            self.state = self.initial
        else:
            self._state = self.initial

    def on_start(self):
        """ Called when the state machine is started (when self.start() is called, immediately before the state is set) """

    def on_end(self):
        """ Called when the state machine is ended (immediately after self.state gets set to None) """

    def _call_function_with_correct_params(self, func, *args, **kwargs):
        """ Call a function with the correct parameters. If the function is a method of this class, then
        it will be called with the state machine instance as the first argument. Otherwise, it will be
        called as is. Also, it will only attempt to call the function with the parameters it accepts.
        """
        sig = inspect.signature(func)
        # Cut args down until it fits the signature
        args = args[:len(sig.parameters)]
        # Remove any kwargs that aren't in the signature
        kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        # bound_args = sig.bind_partial(self, *args, **kwargs)
        # bound_args.apply_defaults()
        return func(*args, **kwargs)

    @property
    def finished(self) -> bool:
        return self._state is None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new:State):
        self.set_state(new)

    def set_state(self, new:State, *args, side_effects=True, **kwargs):
        """ Set the state. This is the setter for self.state, but can also be called directly.
        If side_effects is False, then the before/after methods will not be called.
        Any additional parameters will be passed to both the before/after methods and the transition
        methods.
        """
        old = self._state

        if new is None:
            self._state = None
            self.on_end()
            return

        assert isinstance(new, State), f'Invalid state given. Must be a State instance, but got {type(new)}'
        assert new in self.states._states_list, 'Invalid state given. Must be a member of self.states.'

        if side_effects:
            if old is not None:
                if (method := getattr(self, 'after_' + old.name, False)):
                    self._call_function_with_correct_params(method, *args, **kwargs)

            if (method := getattr(self, 'before_' + new.name, False)):
                self._call_function_with_correct_params(method, *args, **kwargs)

        self._state = new

    def next(self, *args, **kwargs):
        """ Transition to the next state. If the next state is a virtual state, then it will
        immediately transition to the state after that.
        Pass along any additional arguments to the transition and side effect methods.
        """
        # Stupid Python not having do-while loops
        do = True
        while not self.finished and (self.state.virtual or do):
            do = False
            # It's can be a method here only breifly, until it returns a state
            # Apparently just adding self like this works
            next_state:State|Callable = self._call_function_with_correct_params(self._transitions[self.state], *args, **kwargs)

            # Keep calling the returned function until it returns a state
            while True:
                try:
                    next_state = self._call_function_with_correct_params(next_state, *args, **kwargs)
                except TypeError:
                    break

            _warning = 'Transition methods must return a transition method, a State, or None'
            # If it returns 2 things, assume the 2nd is a comment for the graphvis graph
            if isinstance(next_state, (list, tuple)):
                assert isinstance(next_state[1], str), _warning
                next_state = next_state[0]

            assert isinstance(next_state, State) or next_state is None, _warning
            # Pass along the args and kwargs, so the before/after methods can use them
            self.set_state(next_state, *args, **kwargs)

    # This would probably be easier and work better if it used ast instead of dis
    @staticmethod
    def get_returns_dis(func):
        # return [instr.argrepr for instr in dis.Bytecode(func) if instr.opname in ("RETURN_CONST", "RETURN_VALUE")]
        rtn = []
        stack = []  # Tracks last loaded values

        for instr in dis.Bytecode(func):
            if instr.opname in {"LOAD_FAST", "LOAD_GLOBAL", "LOAD_DEREF", "LOAD_CONST", 'LOAD_ATTR'}:  # Variable names
                stack.append(instr.argval)
            elif instr.opname == "RETURN_VALUE":
                if stack[-1] is None:
                    stack.pop(-1)
                    continue
                if stack:  # Use last loaded value (var name or literal)
                    rtn.append(stack[-1])
            elif instr.opname == "RETURN_CONST":
                rtn.append(instr.argval)
            elif instr.opname == "BUILD_TUPLE":
                rtn.append((stack.pop(-2), stack.pop(-1)))
                stack.append(None)

        return [((i, '') if type(i) is not tuple else i) for i in rtn]

    # This almost works, but not quite. It wasn't as good of an option as I was hoping
    @staticmethod
    def get_returns_ast(func):
        class ReturnVisitor(ast.NodeVisitor):
            def __init__(self):
                self.returns = {}

            def visit_FunctionDef(self, node):
                """Handles both function definitions and lambdas."""
                self.generic_visit(node)  # Process child nodes

            def visit_Lambda(self, node):
                """Handles lambda functions."""
                return_value = self.extract_value(node.body)
                self.returns[return_value] = None  # Lambdas don't have doc-like comments after return

            def visit_Return(self, node):
                """Handles return statements and collects potential trailing string literals."""
                return_value = self.extract_value(node.value)
                trailing_string = self.get_trailing_string(node)
                self.returns[return_value] = trailing_string

            def extract_value(self, node):
                """Extracts literals or variable names from AST nodes."""
                if isinstance(node, ast.Constant):  # Literal values (numbers, strings, etc.)
                    return node.value
                elif isinstance(node, ast.Name):  # Variables
                    return node.id
                return "<unknown>"

            def get_trailing_string(self, node):
                """Finds a string literal immediately following a return statement."""
                parent = node.parent
                if parent:
                    body = parent.body
                    try:
                        node_index = body.index(node)
                    except ValueError:
                        body = parent.orelse
                        try:
                            node_index = body.index(node)
                        except ValueError:
                            print('Comment in unhandled place')
                            return
                    if node_index + 1 < len(body):
                        next_node = body[node_index + 1]
                        if isinstance(next_node, ast.Expr) and isinstance(next_node.value, ast.Constant):
                            if isinstance(next_node.value.value, str):  # Must be a string
                                return next_node.value.value
                return None

        source = inspect.getsource(func)
        tree = ast.parse(source)

        # Set parent references for easy access
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

        visitor = ReturnVisitor()
        visitor.visit(tree)
        return visitor.returns

    def construct_graphvis(self,
                           use_names=True,
                           state_kwargs=dict(shape='box'),
                           transition_kwargs=dict(shape='circle'),
                           end_kwargs=dict(shape='triangle'),
                           _backend:Literal['dis', 'ast']='dis',
        ) -> graphviz.Digraph:
        # optionally be disconnect virtual states
        dot = graphviz.Digraph(comment='State Machine')

        def add_function_outputs(trans):
            if _backend == 'dis':
                items = DynamicStateMachine.get_returns_dis(trans)
            elif _backend == 'ast':
                items = DynamicStateMachine.get_returns_ast(trans).items()

            print(items)

            for ret, comment in items:
                if ret is None:
                    dot.node('End', 'End', **end_kwargs)
                    dot.edge(trans.__name__, 'End', comment)
                elif ret in [i.name for i in self.states._states_list]:
                    state = self.states._states[ret]
                    dot.edge(trans.__name__, state.name if use_names else state.value, comment)
                # It's a function
                elif hasattr(self, ret):
                    dot.edge(trans.__name__, ret, comment)
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
            dot.node(state.name, label, **state_kwargs)
            if state._simple:
                dot.edge(state.name, state._simple.name)
            # If it's not simple, then it's a function
            else:
                dot.node(transition.__name__, transition.__name__, **transition_kwargs)
                dot.edge(state.name, transition.__name__)

                add_function_outputs(transition)

        return dot

    def __next__(self):
        self.next()


class ExampleStates(States):
    a = 'this is a'
    b = 'this is b'
    # A virtual State
    pre_c = None
    c = 'this is c'

class ExampleMachine(DynamicStateMachine):
    def __init__(self):
        super().__init__(
            states=ExampleStates,
            initial=ExampleStates.a,
            transitions=(
                # Can be either simple transitions, like so
                ExampleStates.a >> ExampleStates.b,
                # ...or transition methods that determine the next state
                ExampleStates.b >> self.do_the_thing,
                ExampleStates.pre_c >> ExampleStates.c,
                # Transition methods can return a state, another transition method, or None
                ExampleStates.c >> self.decide_if_done,
            )
        )

    def do_the_thing(self, decider=True):
        # Transition methods can have side effects
        print('Deciding...')

        if decider:
            print('Decided on a')
            return ExampleStates.a, 'if decider is True'
        else:
            print('Decided on c')
            return ExampleStates.pre_c

    def decide_if_done(self, done=False):
        print('Deciding if done...')
        if done:
            print('Decided we\'re done')
            return None, 'Im done talking to you now.'
        else:
            print('Decided we\'re not done')
            return ExampleStates.a, 'no keep going!'

    def before_a(self):
        print('Now in state a...', end=' ')

    def after_a(self):
        print('done')

    def before_b(self):
        print('Now in state b...', end=' ')

    def after_b(self):
        print('done')

    def before_c(self):
        print('Now in state c...', end=' done\n')

    # Before/after methods are optional

    def before_pre_c(self):
        print('Now in state pre_c, but not for long...', end=' ')

    def after_pre_c(self):
        print('done')

    def on_start(self):
        print('Starting...')

    def on_end(self):
        print('Finished!')


if __name__ == "__main__":
    # Initial state is a
    m = ExampleMachine()
    # Starting...
    m.next()      # a -> b
    m.next(False) # b -> c
    m.next(False) # c -> a
    next(m)       # a -> b
    m.next(True)  # b -> a
    next(m)       # a -> b
    m.next(False) # b -> c
    m.next(True)  # c -> None
    # Finished!
