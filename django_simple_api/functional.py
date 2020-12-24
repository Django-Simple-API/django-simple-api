from http import HTTPStatus
from types import MethodType
from typing import Type, TypeVar, Any, Callable, Union, Awaitable, Dict
from inspect import signature

from pydantic import BaseModel, create_model

from .fields import PathInfo, QueryInfo, HeaderInfo, CookieInfo, BodyInfo

T = TypeVar("T", Callable[..., Any], Callable[..., Awaitable[Any]])


def bind_params(view_func: T) -> T:
    if hasattr(view_func, "__params__"):
        return view_func

    def bind(real_func: T):

        func: T
        if isinstance(real_func, MethodType):
            func = real_func.__func__
        else:
            func = real_func

        sig = signature(func)
        __params__ = {}
        path, query, header, cookie, body, other = {}, {}, {}, {}, {}, {}  # type: ignore

        for name, param in sig.parameters.items():
            # 忽略部分参数
            if name in ("self", "request", "args", "kwargs", "*args", "**kwargs"):
                continue

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
            elif isinstance(default, PathInfo):
                _type_ = path
            else:
                # 未标注类型的参数会被丢弃
                _type_ = other

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

    if hasattr(view_func, "view_class"):
        view_class = view_func.view_class
        allow_methods = view_class.http_method_names

        funcs = [getattr(view_class, method) for method in allow_methods if hasattr(view_class, method)]

        for cls_func in funcs:
            bind(cls_func)

        setattr(view_func, "__params__", {"flag": "In the class-view, '__params__' attribute is only used as a mark, "
                                                  "which means that the parameters of this class-view have been parsed."})
        return view_func
    else:
        bind(view_func)
    return view_func


def describe_response(
    status: Union[int, HTTPStatus],
    description: str = "",
    *,
    content: Union[Type[BaseModel], dict] = None,
    headers: dict = None,
    links: dict = None,
) -> Callable[[T], T]:
    """
    describe a response in HTTP view function
    https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#responseObject
    """
    status = int(status)
    if not description:
        description = HTTPStatus(status).description

    def decorator(func: T) -> T:
        if not hasattr(func, "__responses__"):
            responses: Dict[int, Dict[str, Any]] = {}
            setattr(func, "__responses__", responses)
        else:
            responses = getattr(func, "__responses__")
        responses[status] = {"description": description}

        if content is not None:
            responses[status]["content"] = content
        if headers is not None:
            responses[status]["headers"] = headers
        if links is not None:
            responses[status]["links"] = links

        return func

    return decorator


def describe_responses(responses: Dict[int, dict]) -> Callable[[T], T]:
    """
    describe responses in HTTP view function
    """

    def decorator(func: T) -> T:
        for status, info in responses.items():
            func = describe_response(status, **info)(func)
        return func

    return decorator
