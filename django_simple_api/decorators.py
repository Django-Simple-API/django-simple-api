from http import HTTPStatus
from typing import Type, TypeVar, Any, Callable, Union, Awaitable, Dict, List

from pydantic import BaseModel

T = TypeVar("T", Callable[..., Any], Callable[..., Awaitable[Any]])


def allow_methods(method: Union[str, List[str]]) -> Callable[[T], T]:
    """
    Declare the request methods allowed by the view function.
    """

    if isinstance(method, str):
        methods = [method.upper()]
    elif isinstance(method, list):
        methods = [m.upper() for m in method]
    else:
        raise TypeError("`method` must be str or list!")

    def wrapper(view_func: T):
        setattr(view_func, "__methods__", methods)
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
    Describe responses in HTTP view function
    """

    def decorator(func: T) -> T:
        for status, info in responses.items():
            func = describe_response(status, **info)(func)
        return func

    return decorator
