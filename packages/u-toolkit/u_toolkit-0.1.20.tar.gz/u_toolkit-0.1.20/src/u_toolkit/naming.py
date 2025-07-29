import re
from collections.abc import Callable
from typing import TypeVar, TypeVarTuple, overload


__all__ = ("to_camel", "to_pascal", "to_snake")

Ts = TypeVarTuple("Ts")
T = TypeVar("T")


def _arguments_handle(transform: Callable, *args, kwd_name: str, **kwds):
    if len(args) > 1:
        return tuple(transform(a) for a in args)

    if args:
        return transform(args[0])

    return transform(kwds[kwd_name])


@overload
def to_pascal(snake: str) -> str: ...
@overload
def to_pascal(*snake: str) -> tuple[str, ...]: ...


def to_pascal(*args, **kwds):
    pattern = re.compile("([0-9A-Za-z])_(?=[0-9A-Z])")

    def transform(arg: str) -> str:
        camel = arg.title()
        return pattern.sub(lambda m: m.group(1), camel)

    return _arguments_handle(transform, *args, kwd_name="snake", **kwds)


@overload
def to_camel(snake: str) -> str: ...
@overload
def to_camel(*snake: str) -> tuple[str, ...]: ...


def to_camel(*args, **kwds):
    # If the string is already in camelCase and does not contain
    # a digit followed by a lowercase letter, return it as it is
    match_pattern = re.compile("^[a-z]+[A-Za-z0-9]*$")
    search_pattern = re.compile(r"\d[a-z]")

    def transform(arg: str):
        if match_pattern.match(arg) and not search_pattern.search(arg):
            return arg

        camel = to_pascal(arg)
        return re.sub("(^_*[A-Z])", lambda m: m.group(1).lower(), camel)

    return _arguments_handle(transform, *args, kwd_name="snake", **kwds)


@overload
def to_snake(camel: str) -> str: ...
@overload
def to_snake(*camel: str) -> tuple[str, ...]: ...


def to_snake(*args, **kwds):
    """Convert a PascalCase, camelCase, kebab-case string to snake_case."""  # noqa: W505

    # Handle the sequence of uppercase letters followed by
    # a lowercase letter
    def transform(arg: str):
        snake = re.sub(
            r"([A-Z]+)([A-Z][a-z])",
            lambda m: f"{m.group(1)}_{m.group(2)}",
            arg,
        )
        # Insert an underscore between a lowercase letter and
        # an uppercase letter
        snake = re.sub(
            r"([a-z])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake
        )
        # Insert an underscore between a digit and an uppercase letter
        snake = re.sub(
            r"([0-9])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake
        )
        # Insert an underscore between a lowercase letter and a digit
        snake = re.sub(
            r"([a-z])([0-9])", lambda m: f"{m.group(1)}_{m.group(2)}", snake
        )
        # Replace hyphens with underscores to handle kebab-case
        snake = snake.replace("-", "_")
        return snake.lower()

    return _arguments_handle(transform, *args, kwd_name="camel", **kwds)
