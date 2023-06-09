import copy
import math
import operator
import typing as t
from contextvars import ContextVar
from functools import partial, wraps

T = t.TypeVar("T")
K = t.TypeVar("K")


def _identity(o: T) -> T:
    return o


def invert_op(operation: t.Callable[[t.Any, t.Any], t.Any]):
    @wraps(operation)
    def _inverterd(self: t.Any, other: t.Any) -> t.Any:
        return operation(other, self)

    return _inverterd


def augmented_op(operation: t.Callable[[t.Any, t.Any], t.Any]):
    @wraps(operation)
    def bind_fn(instance: "Proxy", obj: t.Any) -> t.Any:
        def iop(self: t.Any, other: t.Any) -> "Proxy":
            operation(self, other)
            return instance

        return iop

    return bind_fn


class forward:
    __slots__ = ("_name", "_func", "_class_value", "_bind_fn")

    def __init__(
        self,
        func: t.Union[t.Callable, None] = None,
        class_value: t.Any = None,
        bind_fn: t.Union[
            t.Callable[["Proxy", t.Any], t.Union[t.Callable, None]], None
        ] = None,
    ) -> None:
        self._func = func
        self._class_value = class_value
        if self._class_value is None:
            self._class_value = self
        self._bind_fn = bind_fn

    def bind_fn(
        self, instance: "Proxy", obj: t.Any
    ) -> t.Union[t.Callable, None]:
        if callable(self._bind_fn):
            return self._bind_fn(instance, obj)

        if not callable(self._func):
            return None
        elif hasattr(self._func, "__get__"):
            return self._func.__get__(obj, type(obj))
        else:
            return partial(self._func, obj)

    def __set_name__(self, owner: "Proxy", name: str):
        self._name = name

    def __get__(
        self, instance: "Proxy", owner: t.Union[type, None] = None
    ) -> t.Union[t.Callable, t.Any]:
        if instance is None:
            return self._class_value

        obj = instance._get_current_object()

        ret = self.bind_fn(instance, obj)
        if ret is None:
            ret = getattr(obj, self._name)

        return ret

    def __repr__(self) -> str:
        return f"<ProxyForward({self._name})>"

    def __call__(self, instance: "Proxy", *args, **kwds) -> t.Any:
        return self.__get__(instance, type(instance))(*args, *kwds)


class Proxy(t.Generic[T, K]):
    __slots__ = ("__wrapped", "_get_current_object")
    _get_current_object: t.Callable[[], T]

    @t.overload
    def __init__(self, __local: t.Union[ContextVar[T], t.Callable[[], T]]):
        ...

    @t.overload
    def __init__(
        self,
        __local: t.Union[ContextVar[K], t.Callable[[], K]],
        __getter: t.Callable[[K], T],
    ):
        ...

    def __init__(self, __local, __getter=_identity):
        def _get_current_object():
            if isinstance(__local, ContextVar):
                try:
                    obj = __local.get()
                except LookupError:
                    raise RuntimeError("Unbound context") from None
            elif callable(__local):
                obj = __local()
            else:
                raise TypeError(f"Don't know how to proxy '{type(__local)}'.")

            return __getter(obj)

        object.__setattr__(self, "_get_current_object", _get_current_object)
        object.__setattr__(self, "_Proxy__wrapped", __local)

    # Attributes
    __doc__ = forward()  # type: ignore
    __class__ = forward()  # type: ignore
    __module__ = forward()  # type: ignore
    __dict__ = forward()  # type: ignore
    __annotations__ = forward()  # type: ignore
    __bases__ = forward()  # type: ignore

    # Common
    __repr__ = forward(repr)  # type: ignore
    __str__ = forward(str)  # type: ignore
    __bytes__ = forward(bytes)  # type: ignore
    __format__ = forward()  # type: ignore
    __hash__ = forward(hash)  # type: ignore
    __dir__ = forward(dir)  # type: ignore
    __getattr__ = forward(getattr)  # type: ignore
    # __getattribute__ triggered through __getattr__
    __setattr__ = forward(setattr)  # type: ignore
    __delattr__ = forward(delattr)  # type: ignore
    __instancecheck__ = forward()
    __subclasscheck__ = forward()
    __call__ = forward()

    # Boolean
    __lt__ = forward(operator.lt)
    __le__ = forward(operator.le)
    __eq__ = forward(operator.eq)  # type: ignore
    __ne__ = forward(operator.ne)  # type: ignore
    __gt__ = forward(operator.gt)
    __ge__ = forward(operator.ge)
    __bool__ = forward(bool)

    # Container
    __len__ = forward(len)
    __length_hint__ = forward(operator.length_hint)
    __getitem__ = forward(operator.getitem)
    # __missing__ triggered through __getitem__
    __setitem__ = forward(operator.setitem)
    __delitem__ = forward(operator.delitem)
    __iter__ = forward(iter)
    __next__ = forward(next)
    __reversed__ = forward(reversed)
    __contains__ = forward(operator.contains)

    # Binary Arithmetic Operations
    __add__ = forward(operator.add)
    __sub__ = forward(operator.sub)
    __mul__ = forward(operator.mul)
    __matmul__ = forward(operator.matmul)
    __truediv__ = forward(operator.truediv)
    __floordiv__ = forward(operator.floordiv)
    __mod__ = forward(operator.mod)
    __divmod__ = forward(divmod)
    __pow__ = forward(operator.pow)
    __lshift__ = forward(operator.lshift)
    __rshift__ = forward(operator.rshift)
    __and__ = forward(operator.and_)
    __xor__ = forward(operator.xor)
    __or__ = forward(operator.or_)

    # Binary Arithmetic Operations (swapped)
    __radd__ = forward(invert_op(operator.add))
    __rsub__ = forward(invert_op(operator.sub))
    __rmul__ = forward(invert_op(operator.mul))
    __rmatmul__ = forward(invert_op(operator.matmul))
    __rtruediv__ = forward(invert_op(operator.truediv))
    __rfloordiv__ = forward(invert_op(operator.floordiv))
    __rmod__ = forward(invert_op(operator.mod))
    __rdivmod__ = forward(invert_op(divmod))
    __rpow__ = forward(invert_op(operator.pow))
    __rlshift__ = forward(invert_op(operator.lshift))
    __rrshift__ = forward(invert_op(operator.rshift))
    __rand__ = forward(invert_op(operator.and_))
    __rxor__ = forward(invert_op(operator.xor))
    __ror__ = forward(invert_op(operator.or_))

    # Augmented Arithmetic Assignments
    __iadd__ = forward(invert_op(operator.add))
    __isub__ = forward(invert_op(operator.sub))
    __imul__ = forward(invert_op(operator.mul))
    __imatmul__ = forward(invert_op(operator.matmul))
    __itruediv__ = forward(invert_op(operator.truediv))
    __ifloordiv__ = forward(invert_op(operator.floordiv))
    __imod__ = forward(invert_op(operator.mod))
    __idivmod__ = forward(invert_op(divmod))
    __ipow__ = forward(invert_op(operator.pow))
    __ilshift__ = forward(invert_op(operator.lshift))
    __irshift__ = forward(invert_op(operator.rshift))
    __iand__ = forward(invert_op(operator.and_))
    __ixor__ = forward(invert_op(operator.xor))
    __ior__ = forward(invert_op(operator.or_))

    # Unary Arithmetic Operations
    __neg__ = forward(operator.neg)
    __pos__ = forward(operator.pos)
    __abs__ = forward(operator.abs)
    __invert__ = forward(operator.invert)

    # Complex/Int/Float
    __complex__ = forward(complex)
    __int__ = forward(int)
    __float__ = forward(float)

    # Index
    __index__ = forward(operator.index)

    # round(), trunc(), floor() & ceil()
    __round__ = forward(round)
    __trunc__ = forward(math.trunc)
    __floor__ = forward(math.floor)
    __ceil__ = forward(math.ceil)

    # Context Managers/Coroutines (Async-Await)
    __enter__ = forward()
    __exit__ = forward()
    __await__ = forward()
    __aiter__ = forward()
    __anext__ = forward()
    __aenter__ = forward()
    __aexit__ = forward()

    # Copy
    __copy__ = forward(copy.copy)
    __deepcopy__ = forward(copy.deepcopy)
