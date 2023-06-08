import typing as t

if t.TYPE_CHECKING:
    from contextvars import ContextVar, Token
    from types import TracebackType

T = t.TypeVar("T")


class Context(t.Generic[T]):
    __slots__ = ("_var", "_cv_tokens")

    def __init__(self, var: "ContextVar[T]") -> None:
        self._var = var
        self._cv_tokens: t.List[Token] = []

    def push(self):
        self._cv_tokens.append(self._var.set(self))

    def pop(self):
        ctx = self._var.get()
        self._var.reset(self._cv_tokens.pop())

        if ctx is not self:
            raise AssertionError(
                f"Popped wrong app context. ({ctx!r} instead of {self!r})"
            )

    def __enter__(self):
        self.push()
        return self

    def __exit__(
        self, exc_type: "type", exc_value: "BaseException", tb: "TracebackType"
    ):
        self.pop()
