from mercury.automata import DeterministicFiniteTransducer
from mercury.decorators import DeltaFunction, OutputFunction
from mercury.exceptions import InvalidOutputException
from mercury.operations.sets import S


def test_transducer_simple_example():
    # States
    states = S(["q0", "q1", "q2"])
    input_symbols = "abz"
    output_symbols = "xyz"
    initial_state = "q0"
    final_states = ["q2"]

    # Define transitions
    delta = DeltaFunction()

    @delta.definition()
    def _(state: str, next: str):
        if state == "q0" and next == "a":
            return "q1"
        elif state == "q0" and next == "b":
            return "q2"
        elif state == "q1" and next == "b":
            return "q2"
        return "q0"  # Loop or default fallback

    # Define output for each state (Moore: output only depends on current state)
    output_fn = OutputFunction()

    @output_fn.definition()
    def _(state: str, next: str):
        return {"q0": "z", "q1": "x", "q2": "y"}[state]

    # Build transducer
    transducer = DeterministicFiniteTransducer(
        states=states,
        input_symbols=input_symbols,
        output_symbols=output_symbols,
        initial_state=initial_state,
        final_states=final_states,
        transition_function=delta,
        output_function=output_fn,
    )

    # Test it
    assert transducer.transduce_input("a") == "zx"
    assert transducer.transduce_input("ab") == "zxy"
    assert transducer.transduce_input("b") == "zy"
    assert transducer.transduce_input("ba") == "zyz"


def test_password_strength_transducer():
    from itertools import product

    # Boolean state flags: seen_upper, seen_lower, seen_digit, seen_special
    states = S(product([False, True], repeat=4)) | S(["accept"])

    input_symbols = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&*"
    )
    output_symbols = "uld!e"
    initial_state = (False, False, False, False)
    final_states = ["accept"]

    delta = DeltaFunction()
    output_fn = OutputFunction()

    special_chars = set("!@#$%&*")

    @delta.definition()
    def _(
        has_upper: bool, has_lower: bool, has_digit: bool, has_special: bool, next: str
    ):
        if next.isupper():
            has_upper = True
        elif next.islower():
            has_lower = True
        elif next.isdigit():
            has_digit = True
        elif next in special_chars:
            has_special = True
        else:
            return (
                has_upper,
                has_lower,
                has_digit,
                has_special,
            )  # Stay if invalid char

        if all([has_upper, has_lower, has_digit, has_special]):
            return "accept"
        else:
            return (has_upper, has_lower, has_digit, has_special)

    @delta.definition()
    def _(accept: str, next: str):
        return "accept"

    @output_fn.definition()
    def _(
        has_upper: bool, has_lower: bool, has_digit: bool, has_special: bool, next: str
    ):
        return "e"

    @output_fn.definition()
    def _(accept: str, next: str):
        return "!"

    transducer = DeterministicFiniteTransducer(
        states=states,
        input_symbols=input_symbols,
        output_symbols=output_symbols,
        initial_state=initial_state,
        final_states=final_states,
        transition_function=delta,
        output_function=output_fn,
    )

    # Testing some passwords
    assert transducer.transduce_input("abc") == "eeee"
    assert transducer.transduce_input("Abc1*")[-1] == "!"
    assert transducer.transduce_input("A1b@")[-1] == "!"
    assert transducer.transduce_input("Password1!")[-1] == "!"
    assert transducer.transduce_input("123456")[-1] != "!"


def test_invalid_output_function():
    states = S(["a"])

    input_symbols = "a"
    output_symbols = "a"
    initial_state = "a"
    final_states = ["a"]

    delta = DeltaFunction()
    output_fn = OutputFunction()

    @delta.definition()
    def _(state: str, next: str):
        return state

    @output_fn.definition()
    def _(state: str, next: str):
        return "b"

    try:
        __ = DeterministicFiniteTransducer(
            states=states,
            input_symbols=input_symbols,
            output_symbols=output_symbols,
            initial_state=initial_state,
            final_states=final_states,
            transition_function=delta,
            output_function=output_fn,
        )
        assert False, "Expected InvalidOutputException, constructor passed"
    except InvalidOutputException as e:
        assert True
    except Exception as e:
        assert False, f"Expected InvalidOutputException, encountered {e}"
