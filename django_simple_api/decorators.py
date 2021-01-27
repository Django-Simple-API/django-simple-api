import sys
from http import HTTPStatus
from typing import Any, Callable, Dict, List, Type, TypeVar, Union
from inspect import isclass

if sys.version_info >= (3, 9):
    # https://www.python.org/dev/peps/pep-0585/

    from types import GenericAlias

    GenericType = (GenericAlias, type(List[str]))
else:
    GenericType = (type(List[str]),)

from django.views import View

from pydantic import BaseModel, create_model
from pydantic.utils import display_as_type

T = TypeVar("T")


def allow_request_method(method: str) -> Callable[[T], T]:
    """
    Declare the request method allowed by the view function.
    """
    if method not in View.http_method_names:
        raise ValueError(f"`method` must in {View.http_method_names}")

    def wrapper(view_func: T) -> T:
        if isclass(view_func):
            raise TypeError("Can only be used for functions")

        setattr(view_func, "__method__", method.upper())
        return view_func

    return wrapper


def describe_response(
    status: Union[int, HTTPStatus],
    description: str = "",
    *,
    content: Union[Type[BaseModel], dict] = None,
    headers: dict = None,
    links: dict = None,
) -> Callable[[T], T]:
    """
    Describe a response in HTTP view function
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

        if (
            content is None
            or isinstance(content, dict)
            or (
                not isinstance(content, GenericType)
                and isclass(content)
                and issubclass(content, BaseModel)
            )
        ):
            real_content = content
        else:
            real_content = create_model(
                f"ParsingModel[{display_as_type(content)}]", __root__=(content, ...)
            )

        response = {
            "description": description,
            "content": real_content,
            "headers": headers,
            "links": links,
        }
        responses[status] = {k: v for k, v in response.items() if v}

        return func

    return decorator


def describe_responses(responses: Dict[int, dict]) -> Callable[[T], T]:
    """
    Describe responses in HTTP view function
    """

    def decorator(func: T) -> T:
        for status, info in responses.items():
            func = describe_response(status, **info)(func)
        return func

    return decorator
