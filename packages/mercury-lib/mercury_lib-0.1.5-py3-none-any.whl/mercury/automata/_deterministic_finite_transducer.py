from collections.abc import Generator, Iterable
from itertools import zip_longest

from mercury.decorators import DeltaFunction, OutputFunction
from mercury.exceptions import InvalidOutputException
from mercury.types import InputState, InputSymbol

from ._deterministic_finite_automata import DeterministicFiniteAutomata


class DeterministicFiniteTransducer(DeterministicFiniteAutomata):
    """
    A deterministic finite transducer (DFT) modeled as a Mealy machine.

    This class extends a DFA by adding output behavior, associating each state
    with an output symbol. It is defined using a transition function for state
    changes and an output function for determining outputs.

    Attributes:
        automata: The underlying DFA base instance.
        internal_states: A set containing string representations of internal states.
        input_symbols: A collection of allowed input symbols as strings.
        output_symbols: A collection of output symbols as strings.
        initial_state: String representation of the initial state.
        final_states: Set of string representations of accepting states.
        transition_function: A function mapping current states and input symbols to next states.
        output_function: A function mapping states to output symbols, representing Mealy-style outputs.
    """

    _output_symbols: frozenset[str]
    _output_function: OutputFunction

    def __init__(
        self,
        states: Iterable[InputState],
        input_symbols: Iterable[InputSymbol],
        output_symbols: Iterable[str],
        initial_state: InputState,
        final_states: Iterable[InputState],
        transition_function: DeltaFunction,
        output_function: OutputFunction,
    ) -> None:
        """
        Initialize the DFT (Mealy machine) with the specified states, input/output symbols,
        initial state, accepting states, transition function, and output function.

        Args:
            states: An iterable of all possible internal states (strings).
            input_symbols: An iterable of allowed input symbols.
            output_symbols: An iterable of possible output symbols (strings).
            initial_state: String representation of the initial state.
            final_states: An iterable containing string representations of accepting states.
            transition_function: A DeltaFunction mapping current states and input symbols to next states.
            output_function: An OutputFunction mapping states to output symbols.
        """
        super().__init__(
            states, input_symbols, initial_state, final_states, transition_function
        )
        self._output_symbols = frozenset(output_symbols)
        self._output_function = output_function

        for state in self.states:
            for symbol in self._input_symbols:
                output_symbol = self._output_function(args=state, next_symbol=symbol)
                if output_symbol not in self._output_symbols:
                    raise InvalidOutputException(
                        state, symbol, list(self._output_symbols), output_symbol
                    )

    def read_input_transducer_stepwise(
        self, input_str: str
    ) -> Generator[str, None, None]:
        "Returns a generator that yields each input while reading from the input string"

        state_generator = self.read_input_stepwise(input_str)

        def generator():
            for next_state, next_symbol in zip_longest(state_generator, input_str):
                yield self._output_function(args=next_state, next_symbol=next_symbol)

        return generator()

    def transduce_input(self, input_str: str) -> str:
        """
        Returns the result from the automata after transducing from the input string
        """
        tape = ""
        for output_symbol in self.read_input_transducer_stepwise(input_str):
            tape += output_symbol
        return tape
