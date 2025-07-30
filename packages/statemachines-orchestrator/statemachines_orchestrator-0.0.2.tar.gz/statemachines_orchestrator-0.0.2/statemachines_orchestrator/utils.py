import sys
from functools import lru_cache
from types import FunctionType
from typing import Any


class _MISSING:
    pass


MISSING = _MISSING()


def _create_fn(
    name: str,
    args: list[str],
    body: list[str],
    *,
    globals: dict[str, Any],
    locals: dict[str, Any],
    return_type: Any = MISSING,
) -> FunctionType:
    """
    This function is heavily inspired by dataclasses._create_fn.

    It allows to generate a function with a specific signature and body.
    """

    return_annotation = ""
    if return_type is not MISSING:
        locals["__orchestrator_return_type"] = return_type
        return_annotation = "-> __orchestrator_return_type"
    args_str: str = ", ".join(args)
    body_str: str = "\n".join(f"  {b}" for b in body)

    txt = f" def {name}({args_str}){return_annotation}:\n{body_str}"

    local_vars = ", ".join(locals.keys())
    txt = f"def __create_fn__({local_vars}):\n{txt}\n return {name}"

    ns: dict = {}
    exec(txt, globals, ns)  # this call will create our new function in the ns namespace
    return ns["__create_fn__"](**locals)


def _set_new_attribute(cls: type, fn_name: str, fn: FunctionType) -> None:
    """
    This function is heavily inspired by dataclasses._set_new_attribute

    It allows to set/override a new attribute on a class.
    """
    setattr(cls, fn_name, fn)
    if isinstance(getattr(cls, fn_name), FunctionType):
        # Ensure that the functions returned from _create_fn uses the proper
        # __qualname__ (the class they belong to).
        getattr(cls, fn_name).__qualname__ = f"{cls.__qualname__}.{fn_name}"


def _get_machines_annotations(
    cls: type,
    cls_annotations: dict[str, Any],
) -> dict[str, type]:
    return {
        machine_name: _get_class(cls, machine_name, cls_annotations[machine_name])
        for machine_name in cls_annotations
    }


@lru_cache
def _get_types(cls: type) -> dict[str, type]:
    typing = sys.modules.get("typing")
    if typing is None:
        raise ModuleNotFoundError("typing module is not installed")
    return typing.get_type_hints(cls)


def _get_class(cls: type, machine_name: str, type_or_type_name: str | type) -> type:
    if isinstance(type_or_type_name, type):
        return type_or_type_name
    else:
        return _get_types(cls)[machine_name]
