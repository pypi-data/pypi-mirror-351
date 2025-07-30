from typing import Callable

from ._state import InputState

type Registry = dict[tuple[type, ...], Callable[..., InputState]]
