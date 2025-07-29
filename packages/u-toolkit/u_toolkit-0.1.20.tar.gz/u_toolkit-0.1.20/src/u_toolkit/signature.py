import inspect
from collections.abc import Callable, Sequence
from functools import partial, update_wrapper
from typing import Annotated, Any, NamedTuple, overload


class _Undefined: ...


def list_parameters(fn: Callable, /) -> list[inspect.Parameter]:
    signature = inspect.signature(fn)
    return list(signature.parameters.values())


class WithParameterResult(NamedTuple):
    parameters: list[inspect.Parameter]
    parameter: inspect.Parameter
    parameter_index: int


@overload
def with_parameter(
    fn: Callable, *, name: str, annotation: type | Annotated
) -> WithParameterResult: ...
@overload
def with_parameter(
    fn: Callable, *, name: str, default: Any
) -> WithParameterResult: ...
@overload
def with_parameter(
    fn: Callable, *, name: str, annotation: type | Annotated, default: Any
) -> WithParameterResult: ...


def with_parameter(
    fn: Callable,
    *,
    name: str,
    annotation: type | Annotated | _Undefined = _Undefined,
    default: Any = _Undefined,
) -> WithParameterResult:
    kwargs = {}
    if annotation is not _Undefined:
        kwargs["annotation"] = annotation
    if default is not _Undefined:
        kwargs["default"] = default

    parameters = list_parameters(fn)
    parameter = inspect.Parameter(
        name=name, kind=inspect.Parameter.KEYWORD_ONLY, **kwargs
    )
    index = -1
    if parameters and parameters[index].kind == inspect.Parameter.VAR_KEYWORD:
        parameters.insert(index, parameter)
        index = -2
    else:
        parameters.append(parameter)

    return WithParameterResult(parameters, parameter, index)


def add_parameter(
    fn: Callable,
    *,
    name: str,
    annotation: type | Annotated = _Undefined,
    default: Any = _Undefined,
):
    """添加参数, 会将添加参数后的新函数返回"""
    p = with_parameter(
        fn,
        name=name,
        annotation=annotation,
        default=default,
    )

    new_fn = update_wrapper(partial(fn), fn)
    update_parameters(fn, parameters=p.parameters)
    return new_fn


def update_signature(
    fn: Callable,
    *,
    parameters: Sequence[inspect.Parameter] | None = _Undefined,  # type: ignore
    return_annotation: type | None = _Undefined,
):
    signature = inspect.signature(fn)
    if parameters is not _Undefined:
        signature = signature.replace(parameters=parameters)
    if return_annotation is not _Undefined:
        signature = signature.replace(return_annotation=return_annotation)

    setattr(fn, "__signature__", signature)


def update_parameters(
    fn: Callable,
    *,
    parameters: Sequence[inspect.Parameter] | None = _Undefined,  # type: ignore
):
    update_signature(fn, parameters=parameters)


def update_return_annotation(
    fn: Callable,
    *,
    return_annotation: type | None = _Undefined,
):
    update_signature(fn, return_annotation=return_annotation)
