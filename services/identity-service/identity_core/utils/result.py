from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Success[T]:
    value: T
    is_success: bool = True


@dataclass(frozen=True)
class Failure[E]:
    error: E
    is_success: bool = False


Result = Success[T] | Failure[E]
