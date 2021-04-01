from inspect import isclass, signature
from typing import Any, Callable, Dict, List, Type, TypeVar

from django.http.request import HttpRequest
from pydantic import BaseConfig, BaseModel, ValidationError, create_model

from ._fields import FieldInfo
from .exceptions import RequestValidationError
from .utils import is_class_view, merge_query_dict

HTTPHandler = TypeVar("HTTPHandler", bound=Callable)


def create_model_config(title: str = None, description: str = None) -> Type[BaseConfig]:
    class ExclusiveModelConfig(BaseConfig):
        schema_extra = {
            k: v
            for k, v in {"title": title, "description": description}.items()
            if v is not None
        }

    return ExclusiveModelConfig


def verify_params(
    handler: Any, request: HttpRequest, may_path_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Verify the parameters, and convert the parameters to the corresponding type.
    """
    if is_class_view(handler):
        return _verify_params(
            getattr(
                handler.view_class,
                request.method.lower(),
                handler.view_class.http_method_not_allowed,
            ),
            request,
            may_path_params,
        )
    return _verify_params(handler, request, may_path_params)


def parse_and_bound_params(handler: Any) -> None:
    """
    Get the parameters from the function signature and bind them to the properties of the function
    """
    if is_class_view(handler):
        view_class = handler.view_class
        for method in view_class.http_method_names:
            if not hasattr(view_class, method):
                continue
            setattr(
                view_class, method, _parse_and_bound_params(getattr(view_class, method))
            )
    else:
        _parse_and_bound_params(handler)


def _parse_and_bound_params(handler: HTTPHandler) -> HTTPHandler:
    sig = signature(handler)

    __parameters__: Dict[str, Any] = {
        "path": {},
        "query": {},
        "header": {},
        "cookie": {},
        "body": {},
    }
    __exclusive_models__ = {}

    for name, param in sig.parameters.items():
        default = param.default
        annotation = param.annotation

        if default == param.empty or not isinstance(default, FieldInfo):
            continue

        if getattr(default, "exclusive", False):
            if isclass(annotation) and issubclass(annotation, BaseModel):
                model = annotation
            else:
                model = create_model(
                    "temporary_exclusive_model",
                    __config__=create_model_config(default.title, default.description),
                    __root__=(annotation, ...),
                )
            __parameters__[default._in] = model
            __exclusive_models__[model] = name
            continue

        if isclass(__parameters__[default._in]) and issubclass(
            __parameters__[default._in], BaseModel
        ):
            raise RuntimeError(
                f"{default._in.capitalize()}(exclusive=True) "
                "and {default._in.capitalize()} cannot be used at the same time"
            )

        if annotation != param.empty:
            __parameters__[default._in][name] = (annotation, default)
        else:
            __parameters__[default._in][name] = default

    for key in tuple(__parameters__.keys()):
        _params_ = __parameters__.pop(key)
        if isclass(_params_) and issubclass(_params_, BaseModel) or not _params_:
            continue
        __parameters__[key] = create_model("temporary_model", **_params_)  # type: ignore

    if "body" in __parameters__:
        setattr(handler, "__request_body__", __parameters__.pop("body"))

    if __parameters__:
        setattr(handler, "__parameters__", __parameters__)

    if __exclusive_models__:
        setattr(handler, "__exclusive_models__", __exclusive_models__)

    return handler


def _verify_params(
    handler: HTTPHandler, request: HttpRequest, may_path_params: Dict[str, Any]
) -> Dict[str, Any]:
    parameters = getattr(handler, "__parameters__", None)
    request_body = getattr(handler, "__request_body__", None)
    exclusive_models = getattr(handler, "__exclusive_models__", {})
    if not (parameters or request_body):
        return {}

    data: List[Any] = []
    kwargs: Dict[str, Any] = {}

    try:
        # try to get parameters model and parse
        if parameters:
            if "path" in parameters:
                data.append(parameters["path"].parse_obj(may_path_params))

            if "query" in parameters:
                data.append(
                    parameters["query"].parse_obj(merge_query_dict(request.GET))
                )

            if "header" in parameters:
                data.append(parameters["header"].parse_obj(request.headers))

            if "cookie" in parameters:
                data.append(parameters["cookie"].parse_obj(request.COOKIES))

        # try to get body model and parse
        if request_body:
            data.append(request_body.parse_obj(request.DATA))

    except ValidationError as e:
        raise RequestValidationError(e)

    for _data in data:
        if _data.__class__.__name__ == "temporary_model":
            kwargs.update(_data.dict())
        elif _data.__class__.__name__ == "temporary_exclusive_model":
            kwargs[exclusive_models[_data.__class__]] = _data.__root__
        else:
            kwargs[exclusive_models[_data.__class__]] = _data

    return kwargs
