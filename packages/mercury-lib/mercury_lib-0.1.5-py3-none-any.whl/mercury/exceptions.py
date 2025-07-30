from collections.abc import Hashable
from inspect import Parameter
from typing import Callable

from mercury.types import Registry


class MissingTypeHintException(Exception):

    def __init__(self, parameters: list[Parameter]) -> None:
        trobule_parameters = [
            p.name
            for p in parameters
            if p.default == p.empty  # pyright: ignore[reportAny]
        ]
        super().__init__(f"Missing type hint for parameters: {trobule_parameters}")


class MissingNextParameterException(Exception):
    def __init__(
        self,
        func: Callable[..., tuple[Hashable, ...] | Hashable],
    ) -> None:
        super().__init__(
            f"Missing parameter `next` in {func.__name__} for DeltaFunction()"
        )


class MissingStateException(Exception):
    def __init__(
        self, state: tuple[Hashable], symbol: str, next_state: tuple[Hashable]
    ) -> None:
        super().__init__(
            f"Could not transition from state {state}, symbol {symbol}, to {next_state}, because {next_state} is not a valid state in the definition of the automata"
        )


class MissingDefinitionException(Exception):
    def __init__(
        self, registry: Registry, state: tuple[Hashable], next_symbol: str
    ) -> None:
        super().__init__(
            f"Could not call the transition from state {state} with symbol {next_symbol}, could not find definition in registry, types defined: {list(registry.keys())}"
        )


class InvalidOutputException(Exception):
    def __init__(
        self,
        state: tuple[Hashable],
        next_symbol: str,
        valid_outputs: list[str],
        found_output: Hashable,
    ) -> None:
        super().__init__(
            f"Could not call the transition from state {state} with symbol {next_symbol}, output function returned value {found_output} which is not part of {valid_outputs}"
        )


class InvalidReturnTypeException(Exception):
    def __init__(
        self,
        caller_name: str,
        expected_type: type,
        recieved_type: type,
        value: Hashable,
    ) -> None:
        super().__init__(
            f"Could not return from {caller_name}, expected to return type {expected_type.__name__}, recieved {value} of type {recieved_type.__name__} instead"
        )


class WrongArgumentException(Exception):
    def __init__(self, expected_class: type, found_class: type) -> None:
        super().__init__(
            f"Expected to find class '{expected_class.__name__}' as input, recieved '{found_class.__name__}' instead"
        )
