from typing import (
    TypeVar,
    Callable,
    Coroutine,
    AsyncGenerator,
    AsyncIterator,
    Generator,
)

RETURN_TYPE = TypeVar("RETURN_TYPE")

DependencyCallable = Callable[
    ...,
    RETURN_TYPE
    | Coroutine[None, None, RETURN_TYPE]
    | AsyncGenerator[RETURN_TYPE, None]
    | Generator[RETURN_TYPE, None, None]
    | AsyncIterator[RETURN_TYPE],
]

ID = TypeVar("ID")
