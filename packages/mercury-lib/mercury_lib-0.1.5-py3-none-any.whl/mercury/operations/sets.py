from collections.abc import Set
from typing import Hashable, TypeVar, override

T = TypeVar("T", bound=Hashable)
U = TypeVar("U", bound=Hashable)


class S(frozenset[T]):
    """
    A simplified frozenset, used for quick operations in the Mercury library

    S works just like a regular frozenset (meaning a set that cannot be modified directly),
    save for implementing both product and union operations using the traditional operations
    * and |, as to make syntax easier to read and use by students.

    Examples with more detail on how to use S are in the documentation page. You may also use
    regular collections instead of this set on automata, these were made to be convenient to translate
    old GOLD-3 syntax and exercises into this newer version.

    Basic usage:
    ```python
        S({'a', 'b'}) * S({0}) # yields {('a', 0), ('b', 0)}
        S({'a', 'b'}) * S(range(3)) # yields {('a', 0), ('a', 1), ('a', 2) ('b', 0), ('b', 1), ('b', 2)}
        S({'a', 'b'}) | S(range(3)) # yields {('a'), ('b'), (0), (1), (2)}
    ```
    """

    def __mul__(self, other: "S[U]") -> "S[tuple[T, U]]":
        return S((a, b) for a in self for b in other)

    @override
    def __or__(self, other: "Set[Hashable]") -> "S[Hashable]":
        return S(super().__or__(other))
