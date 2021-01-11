from typing import TypeVar, Callable, Awaitable, Dict, List, Any
from inspect import signature, isclass
from functools import partial

from django.http.request import QueryDict
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from pydantic import BaseModel, ValidationError, create_model

from .utils import merge_query_dict
from .exceptions import RequestValidationError
from .fields import QueryInfo, HeaderInfo, CookieInfo, BodyInfo, PathInfo, ExclusiveInfo

HTTPHandler = TypeVar(
    "HTTPHandler",
    Callable[..., HttpResponse],
    Callable[..., Awaitable[HttpResponse]],
)


def create_model_config(title: str = None, description: str = None):
    class ExclusiveModelConfig:
        @staticmethod
        def schema_extra(schema, model) -> None:
            if title is not None:
                schema["title"] = title
            if description is not None:
                schema["description"] = description

    return ExclusiveModelConfig


def parse_params(function: Callable) -> Callable:
    sig = signature(function)

    __parameters__ = {}
    __exclusive_models__ = {}
    path: Dict[str, Any] = {}
    query: Dict[str, Any] = {}
    header: Dict[str, Any] = {}
    cookie: Dict[str, Any] = {}
    body: Dict[str, Any] = {}

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
        elif isinstance(default, PathInfo):
            _type_ = path
        elif isinstance(default, ExclusiveInfo):
            if isclass(annotation) and issubclass(annotation, BaseModel):
                model = annotation
            else:
                model = create_model(
                    "temporary_exclusive_model",
                    __config__=create_model_config(default.title, default.description),
                    __root__=(annotation, ...),
                )
            __parameters__[default.name] = model
            __exclusive_models__[model] = name
            continue
        else:
            continue

        if annotation != param.empty:
            _type_[name] = (annotation, default)
        else:
            _type_[name] = default

    __locals__ = locals()
    for key in filter(
        lambda key: bool(__locals__[key]), ("path", "query", "header", "cookie", "body")
    ):
        if key in __parameters__:
            raise RuntimeError(
                f'Exclusive("{key}") and {key.capitalize()} cannot be used at the same time'
            )
        __parameters__[key] = create_model("temporary_model", **locals()[key])  # type: ignore

    if "body" in __parameters__:
        setattr(function, "__request_body__", __parameters__.pop("body"))

    if __parameters__:
        setattr(function, "__parameters__", __parameters__)

    if __exclusive_models__:
        setattr(function, "__exclusive_models__", __exclusive_models__)

    return function


async def bound_params(handler: Callable, request: HttpRequest) -> Callable:
    """
    bound parameters "path", "query", "header", "cookie", "body" to the view function
    """
    parameters = getattr(handler, "__parameters__", None)
    request_body = getattr(handler, "__request_body__", None)
    exclusive_models = getattr(handler, "__exclusive_models__", {})
    if not (parameters or request_body):
        return handler

    data: List[Any] = []
    kwargs: Dict[str, BaseModel] = {}

    try:
        # try to get parameters model and parse
        if parameters:
            if "path" in parameters:
                data.append(parameters["path"].parse_obj(request.path_params))

            if "query" in parameters:
                data.append(
                    parameters["query"].parse_obj(
                        merge_query_dict(request.query_params.multi_items())
                    )
                )

            if "header" in parameters:
                data.append(
                    parameters["header"].parse_obj(
                        merge_query_dict(request.headers.items())
                    )
                )

            if "cookie" in parameters:
                data.append(parameters["cookie"].parse_obj(request.cookies))

        # try to get body model and parse
        if request_body:
            _body_data = request.DATA
            if isinstance(_body_data, QueryDict):
                _body_data = merge_query_dict(_body_data)
            data.append(request_body.parse_obj(_body_data))

    except ValidationError as e:
        raise RequestValidationError(e)

    for _data in data:
        if _data.__class__.__name__ == "temporary_model":
            kwargs.update(_data.dict())
        elif _data.__class__.__name__ == "temporary_exclusive_model":
            kwargs[exclusive_models[_data.__class__]] = _data.__root__
        else:
            kwargs[exclusive_models[_data.__class__]] = _data
    return partial(handler, **kwargs)
