import inspect
from collections.abc import Hashable
from types import NoneType
from typing import Callable, cast

from mercury.exceptions import (
    MissingDefinitionException,
    MissingNextParameterException,
    MissingTypeHintException,
)
from mercury.types import InputState, Registry

NEXT_SYMBOL_KEYWORD_NAME = "next"


class DeltaFunction:
    """
    Creates a new delta function instance for an automata to use

    A delta function is a function that an automata can use in order
    to create transitions between states based on the next character
    read by the machine. This function can have one or more definitions
    such that it can handle different lengths of tuples in expected states
    """

    _registry: Registry

    def __init__(self) -> None:
        self._registry = {}

    def __call__(
        self,
        args: tuple[Hashable],
        next_symbol: str,
    ):
        type_args = tuple([type(arg) for arg in args])

        if type_args not in self._registry:
            raise MissingDefinitionException(self._registry, args, next_symbol)

        resolver = self._registry[type_args]

        return resolver(*args, **{NEXT_SYMBOL_KEYWORD_NAME: next_symbol})

    def definition(self):
        """
        Declares the following function as part of a delta function,
        and adds it to it's definition table

        For a DFA to be able to work with multiple functions in python, we use
        the `DeltaFunction()` helper, which allows us to give a function more than
        one definition in order to handle states that can be tuples of 1, 2 or
        more values, and that need to be handled differently depending on how many
        values the tuple has

        To use the function, call it as a decorator on top of the
        definition you wish to use

        Example:

        ```py
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
        ```

        Do know that for convenience, it is recommended to name the functions as `_`
        in order for python to understand that the function will not be called by name,
        but by an external library/caller, such as Mercury. Could help avoid naming warnings in
        traditional LSP implementations of common editors
        """

        def decorator(func: Callable[..., InputState]):
            signature = inspect.signature(func)
            parameters = list(signature.parameters.values())

            if NEXT_SYMBOL_KEYWORD_NAME not in [p.name for p in parameters]:
                raise MissingNextParameterException(func)

            parameters.remove(
                [p for p in parameters if p.name == NEXT_SYMBOL_KEYWORD_NAME][0]
            )

            type_hints = [
                (
                    cast(type, p.annotation)
                    if p.annotation != p.empty  # pyright: ignore[reportAny]
                    else NoneType  # NOTE: This means we don't support (a: NoneType)
                )
                for p in parameters
            ]

            # Report any missing typehints for parameters
            if NoneType in type_hints:
                raise MissingTypeHintException(parameters)

            self._registry[tuple(type_hints)] = func
            return func

        return decorator
