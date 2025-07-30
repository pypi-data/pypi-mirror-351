from collections.abc import Hashable

type State = tuple[Hashable]
"""
States are the core foundation of DFAs inside of Mercury. These states are simple tuples
of hashable values. Since `automata-python` can only handle states in string format,
states from `mercury` need to be translated to strings using the python `repr` function.

Do not confuse them with InputState, which are states solely used to provide flexibility
in the constructor such that it's easier to use, but will not be returned by the automaton
at any point
"""

type InputState = State | Hashable
"""
InputStates are simple abstractions that make it easier for users to provide states
in multiple formats to Deterministic automata. These are usually just hashable values.
If the input state is a tuple, it will be treated as a regular state for state management,
otherwise, it will be converted internally into a one-valued tuple as to make transition
function management easier
"""

type InputSymbol = str
"""
Wrapper over string to represent a single input symbol. It should always be a one-character
string value, however, this verification might not be enforced at runtime for now
"""
