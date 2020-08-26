from typing import TypeVar, Any, Callable, Union
from inspect import signature
from http import HTTPStatus

from pydantic import create_model

from .fields import PathInfo, QueryInfo, HeaderInfo, CookieInfo, BodyInfo

T = TypeVar("T")


def bound_params(func: T) -> T:
    """
    parse function annotation to pydantic.BaseModel,
    and bound them in `func.__params__`.
    """
    if hasattr(func, "__params__"):
        return func

    sig = signature(func)
    __params__ = {}
    path, query, header, cookie, body = {}, {}, {}, {}, {}

    for name, param in sig.parameters.items():
        default = param.default
        annotation = param.annotation

        if isinstance(default, QueryInfo):
            _type_ = query
        elif isinstance(default, HeaderInfo):
            _type_ = header
        elif isinstance(default, CookieInfo):
            _type_ = cookie
        elif isinstance(default, BodyInfo):
            _type_ = body
        elif isinstance(default, PathInfo) or default == param.default:
            _type_ = path

        if annotation != param.empty:
            if default == param.empty:
                _type_[name] = (annotation, ...)
            else:
                _type_[name] = (annotation, default)
        elif default != param.empty:
            _type_[name] = default

    for key in ("path", "query", "header", "cookie", "body"):
        if locals()[key]:
            __params__[key] = create_model(f"temporary_{key}", **locals()[key])

    setattr(func, "__params__", __params__)
    return func


def describe_response(
    status: Union[int, HTTPStatus], response_model: Any = None, description: str = "",
) -> Callable[[T], T]:
    """bind status => response model in http handler"""

    def decorator(func: T) -> T:
        """bind response model"""
        if hasattr(func, "__responses__"):
            getattr(func, "__responses__")[status] = {"model": response_model}
        else:
            setattr(func, "__responses__", {status: {"model": response_model}})
        getattr(func, "__responses__")[status]["description"] = description
        return func

    return decorator
