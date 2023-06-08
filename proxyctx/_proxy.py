import typing as t
from contextvars import ContextVar
from functools import wraps

_PROXIED_ATTRIBUTES = [
    "__doc__",
    "__class__",
]

_PROXIED = [
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


def _proxy_method(__name: str, __get_self: "t.Callable[[], T]"):
    method_code = (
        "def {name}(_, *args, **kwargs):"
        "\n\treturn _get_self().{name}(*args, **kwargs)".format(name=__name)
    )

    ns: t.Dict[str, t.Any] = {}
    exec(method_code, {"_get_self": __get_self}, ns)
    return ns[__name]


@t.overload
def proxy(__local: t.Union["ContextVar[T]", "t.Callable[[], T]"]) -> T:
    ...


@t.overload
def proxy(
    __local: t.Union["ContextVar[K]", "t.Callable[[], K]"],
    __getter: t.Callable[[K], T],
) -> T:
    ...


def proxy(__local, __getter=None):
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

    namespace = {"__wrapped": __local, "__slots__": ("__wrapped")}
    for key in _PROXIED:
        namespace[key] = _proxy_method(key, _get_current_object)

    namespace["__getattribute__"] = _proxy_method(
        "__getattribute__", _get_current_object
    )
    cls = type("Proxy", tuple(), namespace)
    return cls()
