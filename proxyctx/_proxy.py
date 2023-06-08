import typing as t
from contextvars import ContextVar
from functools import wraps

_PROXIED = [
    "__doc__",
    "__repr__",
    "__str__",
    "__bytes__",
    "__format__",
    "__lt__",
    "__le__",
    "__eq__",
    "__ne__",
    "__gt__",
    "__ge__",
    "__hash__",
    "__bool__",
    "__getattr__",
    "__setattr__",
    "__delattr__",
    "__dir__",
    "__class__",
    "__instancecheck__",
    "__subclasscheck__",
    "__call__",
    "__len__",
    "__length_hint__",
    "__getitem__",
    "__setitem__",
    "__delitem__",
    "__iter__",
    "__next__",
    "__reversed__",
    "__contains__",
    "__add__",
    "__sub__",
    "__mul__",
    "__matmul__",
    "__truediv__",
    "__floordiv__",
    "__mod__",
    "__divmod__",
    "__pow__",
    "__lshift__",
    "__rshift__",
    "__and__",
    "__xor__",
    "__or__",
    "__neg__",
    "__pos__",
    "__abs__",
    "__invert__",
    "__complex__",
    "__int__",
    "__float__",
    "__index__",
    "__round__",
    "__trunc__",
    "__floor__",
    "__ceil__",
    "__enter__",
    "__exit__",
    "__await__",
    "__aiter__",
    "__anext__",
    "__aenter__",
    "__aexit__",
    "__copy__",
    "__deepcopy__",
    "__radd__",
    "__rsub__",
    "__rmul__",
    "__rmatmul__",
    "__rtruediv__",
    "__rfloordiv__",
    "__rmod__",
    "__rdivmod__",
    "__rpow__",
    "__rlshift__",
    "__rrshift__",
    "__rand__",
    "__rxor__",
    "__ror__",
    "__iadd__",
    "__isub__",
    "__imul__",
    "__imatmul__",
    "__itruediv__",
    "__ifloordiv__",
    "__imod__",
    "__ipow__",
    "__ilshift__",
    "__irshift__",
    "__iand__",
    "__ixor__",
    "__ior__",
]

T = t.TypeVar("T")
K = t.TypeVar("K")


def _identity(o: T) -> T:
    return o


def _inject_self(__method: "t.Callable", __get_self: "t.Callable"):
    @wraps(__method)
    def _wrapper(_, *args, **kwargs):
        return __method(__get_self(), *args, **kwargs)

    return _wrapper


def _proxy_cls(
    __class: t.Type[T],
    __get_self: "t.Callable[[], T]",
    namespace: t.Union[dict, None] = None,
) -> t.Type[T]:
    class_name = "{}Proxy".format(__class.__name__)

    ns = namespace if namespace else {}
    for key in filter(lambda item: item in dir(__class), _PROXIED):
        wrapped = getattr(__class, key)
        if callable(wrapped):
            ns[key] = _inject_self(wrapped, __get_self)
        else:
            ns[key] = wrapped

    ns["__getattribute__"] = _inject_self(__class.__getattribute__, __get_self)
    return type(class_name, tuple(), ns)


@t.overload
def proxy(
    __class: t.Type[T], __local: t.Union["ContextVar[T]", "t.Callable[[], T]"]
) -> T:
    ...


@t.overload
def proxy(
    __class: t.Type[K],
    __local: t.Union["ContextVar[T]", "t.Callable[[], T]"],
    __getter: t.Callable[[T], K],
) -> K:
    ...


def proxy(__class, __local, __getter=None):
    if __getter is None:
        __getter = _identity

    def _get_current_object():
        if isinstance(__local, ContextVar):
            try:
                obj = __local.get()
            except LookupError:
                raise RuntimeError("Unbound context") from None
        elif t.Callable(__local):
            obj = __local()
        else:
            raise TypeError(f"Don't know how to proxy '{type(__local)}'.")

        return __getter(obj)

    cls = _proxy_cls(
        __class,
        _get_current_object,
        {"__wrapped": __local, "__slots__": ("__wrapped")},
    )
    return cls()
