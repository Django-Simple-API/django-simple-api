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


def _mark_tags_for_view(handler: Any, tags: Union[list, tuple]) -> None:
    describe_extra_docs(handler, {"tags": tags})


def mark_tags_for_urlpatterns(
    urlpatterns: List[Union[URLPattern, URLResolver]], tags: Union[list, tuple]
) -> None:
    for item in urlpatterns:
        if isinstance(item, URLPattern):
            _mark_tags_for_view(item.callback, tags)
        else:
            mark_tags_for_urlpatterns(item.url_patterns, tags)


def mark_tags(*tags: str) -> Callable[[T], T]:
    def wrapper(view: T) -> T:
        if isinstance(view, (list, tuple)):
            # For include(...) processing.
            urlconf_module = view[0]
            urlpatterns = getattr(urlconf_module, "urlpatterns", urlconf_module)
            mark_tags_for_urlpatterns(urlpatterns, tags)
        elif callable(view):
            _mark_tags_for_view(view, tags)
        else:
            raise TypeError('view must be a callable or a list/tuple in the case of include().')
        return view

    return wrapper


def deprecated_mark_tags(obj: T, tags: Union[list, tuple]) -> T:
    if isinstance(obj, tuple):
        urlpatterns = getattr(obj[0], "urlpatterns", [])
        mark_tags_for_urlpatterns(urlpatterns, tags)
    else:
        _mark_tags_for_view(obj, tags)
    return obj
