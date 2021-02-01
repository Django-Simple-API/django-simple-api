from typing import Any, Callable, Dict, Sequence, TypeVar, List, Union

from django.urls import URLPattern, URLResolver

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
    __extra_docs__ = merge_openapi_info(getattr(handler, "__extra_docs__", {}), info)

    if is_class_view(handler):
        view_class = handler.view_class  # type: ignore
        for method in filter(
            lambda method: hasattr(view_class, method), view_class.http_method_names
        ):
            setattr(
                getattr(view_class, method.lower()), "__extra_docs__", __extra_docs__
            )
    else:
        setattr(handler, "__extra_docs__", __extra_docs__)
    return handler


def add_tag_to_view(handler: Any, tags: Union[list, tuple]) -> None:
    describe_extra_docs(handler, {"tags": tags})


def add_tag_urlpatterns(
    urlpatterns: List[Union[URLPattern, URLResolver]], tags: Union[list, tuple]
) -> None:
    for item in urlpatterns:
        if isinstance(item, URLPattern):
            add_tag_to_view(item.callback, tags)
        else:
            add_tag_urlpatterns(item.url_patterns, tags)


def add_tags_1(*tags: str) -> Callable[[T], T]:
    # obj可以是include(),也可以是class-view, func-view
    def wrapper(obj: T) -> T:
        if isinstance(obj, tuple):
            urlpatterns = getattr(obj[0], "urlpatterns", [])
            add_tag_urlpatterns(urlpatterns, tags)
        else:
            add_tag_to_view(obj, tags)
        return obj

    return wrapper


def add_tags_2(obj: T, tags: Union[list, tuple]) -> T:
    if isinstance(obj, tuple):
        urlpatterns = getattr(obj[0], "urlpatterns", [])
        add_tag_urlpatterns(urlpatterns, tags)
    else:
        add_tag_to_view(obj, tags)
    return obj
