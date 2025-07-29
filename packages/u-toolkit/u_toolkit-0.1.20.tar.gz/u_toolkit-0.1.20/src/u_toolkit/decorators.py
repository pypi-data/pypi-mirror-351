import inspect
from collections.abc import Callable
from functools import wraps
from typing import Generic, NamedTuple, ParamSpec, TypeVar


_FnT = TypeVar("_FnT", bound=Callable)

_T = TypeVar("_T")


class DefineMethodParams(NamedTuple, Generic[_T, _FnT]):
    method_class: type[_T]
    method_name: str
    method: _FnT


class DefineMethodDecorator(Generic[_T, _FnT]):
    def __init__(self, fn: _FnT):
        self.fn = fn
        self.name = fn.__name__

    def register_method(self, params: DefineMethodParams[_T, _FnT]): ...

    def __set_name__(self, owner_class: type, name: str):
        self.register_method(DefineMethodParams(owner_class, name, self.fn))

    def __get__(self, instance: _T, owner_class: type[_T]):
        if inspect.iscoroutinefunction(self.fn):

            @wraps(self.fn)
            async def awrapper(*args, **kwargs):
                return await self.fn(instance, *args, **kwargs)

            return awrapper

        @wraps(self.fn)
        def wrapper(*args, **kwargs):
            return self.fn(instance, *args, **kwargs)

        return wrapper


def define_method_handler(
    handle: Callable[[DefineMethodParams[_T, _FnT]], None],
):
    class Decorator(DefineMethodDecorator):
        def register_method(self, params: DefineMethodParams):
            handle(params)

    return Decorator


_P = ParamSpec("_P")

_T2 = TypeVar("_T2")


def create_decorator(
    handle: Callable[_P, _T2] | None = None,
    use_handle_return: bool | None = None,
):
    def decorator(fn: Callable[_P, _T]):
        if inspect.iscoroutinefunction(fn):

            @wraps(fn)
            async def async_wrapper(*args, **kwargs):
                handle_result = None
                if inspect.iscoroutinefunction(handle):
                    handle_result = await handle(*args, **kwargs)
                elif handle:
                    handle_result = handle(*args, **kwargs)
                if use_handle_return:
                    return handle_result
                return await fn(*args, **kwargs)

            return async_wrapper

        @wraps(fn)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs):
            if handle:
                handle_result = handle(*args, **kwargs)
                if use_handle_return:
                    return handle_result

            return fn(*args, **kwargs)

        return wrapper

    return decorator
