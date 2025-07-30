from collections.abc import Hashable
from typing import override

from mercury.exceptions import InvalidReturnTypeException

from ._delta_function import DeltaFunction


class OutputFunction(DeltaFunction):
    """
    Creates a new output function instance for a Moore DFA transducer

    In a Moore transducer (like the one implemented by this library),
    the output function maps each state to an output symbol.

    This function defines what output is produced when the automaton
    enters a given state, independent of the input character being read.
    Multiple definitions can be provided to support expressive mapping
    between states and outputs.

    Rules for the output function are similar to the delta function, but
    you must return an output symbol from the alphabet (usually one character)
    """

    @override
    def __call__(
        self,
        args: tuple[Hashable],
        next_symbol: str,
    ):
        response = super().__call__(args, next_symbol)
        if not isinstance(response, str):
            raise InvalidReturnTypeException(
                "OutputFunction", str, type(response), response
            )
        return response
