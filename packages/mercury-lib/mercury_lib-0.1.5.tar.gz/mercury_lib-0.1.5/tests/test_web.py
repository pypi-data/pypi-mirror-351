from mercury.automata import DeterministicFiniteAutomata
from mercury.decorators import DeltaFunction
from mercury.operations.sets import S
from mercury.web import DFAView


def test_automata_Amod3xBmod3_web_visualization():
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

    web = DFAView(automata)
    # TODO: Some unit testing on the view endpoint would be appreciated
