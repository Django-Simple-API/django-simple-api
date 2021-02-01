from typing import Any, Callable, Dict, Sequence, TypeVar

from .utils import is_class_view

T = TypeVar("T", bound=Callable)


def merge_openapi_info(
    operation_info: Dict[str, Any], more_info: Dict[str, Any]
) -> Dict[str, Any]:
    for key, value in more_info.items():
        if key in operation_info:
            if isinstance(operation_info[key], Sequence):
                operation_info[key] = _ = list(operation_info[key])
                _.extend(value)
                continue
            elif isinstance(operation_info[key], dict):
                operation_info[key] = merge_openapi_info(operation_info[key], value)
                continue
        operation_info[key] = value
    return operation_info


def describe_extra_docs(handler: T, info: Dict[str, Any]) -> T:
    """
    describe more openapi info in HTTP handler

    https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#operationObject
    """
    if is_class_view(handler):
        view_class = handler.view_class  # type: ignore
        for method in filter(
            lambda method: hasattr(view_class, method), view_class.http_method_names
        ):
            handler_method = getattr(view_class, method.lower())
            __extra_docs__ = merge_openapi_info(
                getattr(handler_method, "__extra_docs__", {}), info
            )
            setattr(handler_method, "__extra_docs__", __extra_docs__)
    else:
        __extra_docs__ = merge_openapi_info(
            getattr(handler, "__extra_docs__", {}), info
        )
        setattr(handler, "__extra_docs__", __extra_docs__)
    return handler
