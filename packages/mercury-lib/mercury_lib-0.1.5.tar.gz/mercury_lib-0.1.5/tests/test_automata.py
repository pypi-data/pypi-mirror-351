from frozendict import frozendict

from mercury.automata import DeterministicFiniteAutomata
from mercury.decorators import DeltaFunction
from mercury.exceptions import MissingDefinitionException
from mercury.operations.sets import S


def test_automata_creation():
    states = [0, 1]
    input_symbols = "01"
    initial_state = 0
    final_states = [0]

    delta = DeltaFunction()

    @delta.definition()
    def _(_: int, next: str):
        return int(next)

    __ = DeterministicFiniteAutomata(
        states, input_symbols, initial_state, final_states, delta
    )


def test_automata_simple_scenario():
    states = [0, 1]
    input_symbols = "01"
    initial_state = 0
    final_states = [0]

    delta = DeltaFunction()

    @delta.definition()
    def _(_: int, next: str):
        return int(next)

    automata = DeterministicFiniteAutomata(
        states, input_symbols, initial_state, final_states, delta
    )

    assert automata.accepts_input("010")
    assert automata.accepts_input("1111111111111111110")
    assert not automata.accepts_input("01")
    assert not automata.accepts_input("1")
    assert automata.accepts_input("")


def test_automata_missing_definition():
    states = [0, 1]
    input_symbols = "01"
    initial_state = 0
    final_states = [0]

    delta = DeltaFunction()

    try:
        __ = DeterministicFiniteAutomata(
            states, input_symbols, initial_state, final_states, delta
        )
        assert False, "Expected MissingDefinitionException, constructor passed"
    except MissingDefinitionException as e:
        assert True


def test_automata_properties():
    states = [0, 1]
    input_symbols = "01"
    initial_state = 0
    final_states = [0]

    delta = DeltaFunction()

    @delta.definition()
    def _(_: int, next: str):
        return int(next)

    automata = DeterministicFiniteAutomata(
        states, input_symbols, initial_state, final_states, delta
    )

    assert automata.states == frozenset([(0,), (1,)])
    assert automata.input_symbols == frozenset(["0", "1"])
    assert automata.initial_state == (0,)
    assert automata.final_states == frozenset([(0,)])
    assert automata.transitions == frozendict(
        {((0,), "0"): (0,), ((1,), "0"): (0,), ((0,), "1"): (1,), ((1,), "1"): (1,)}
    )


def test_automata_Amod3xBmod3_scenario():
    states = S({"a", "b"}) * S(range(3)) | S({0})
    input_symbols = "abx"
    initial_state = ("a", 0)
    final_states = [("b", 0)]

    delta = DeltaFunction()

    @delta.definition()
    def _(_: int, next: str):
        return 0

    @delta.definition()
    def _(w: str, y: int, next: str):
        if w == "a" and next == "a":
            return (w, (y + 1) % 3)
        elif w == "a" and next == "b":
            return (w, y)
        elif w == "a" and next == "x":
            return ("b", (3 - y) % 3)
        elif w == "b" and next == "b":
            return (w, (y + 1) % 3)
        elif w == "b" and next == "a":
            return (w, y)
        else:
            return 0

    automata = DeterministicFiniteAutomata(
        states, input_symbols, initial_state, final_states, delta
    )

    assert automata.accepts_input("x")
    assert automata.accepts_input("aaaxbbb")
    assert automata.accepts_input("aaax")
    assert not automata.accepts_input("axbb")
