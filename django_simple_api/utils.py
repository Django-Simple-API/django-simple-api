import re
from typing import Any, Callable, Generator, List, Tuple, Union
from functools import partial

from django.conf import settings
from django.urls import URLPattern, URLResolver
from django.urls.conf import RegexPattern, RoutePattern
from django.http.request import QueryDict

RE_PATH_PATTERN = re.compile(r"\(\?P<(?P<name>\w*)>.*?\)")
PATH_PATTERN = re.compile(r"<(.*?:)?(?P<name>\w*)>")
REPLACE_RE_FLAG_PATTERN = re.compile(r"(?<!\\)\^|(?<!\\)\$")


def _reformat_pattern(pattern: Union[RoutePattern, RegexPattern]) -> str:
    path_format = str(pattern)
    if isinstance(pattern, RoutePattern):
        pattern = PATH_PATTERN
    else:  # RegexPattern
        path_format = re.sub(REPLACE_RE_FLAG_PATTERN, "", path_format)
        pattern = RE_PATH_PATTERN
    return re.sub(pattern, r"{\g<name>}", path_format)


def get_urls(
    urlpatterns: List[Union[URLPattern, URLResolver]],
    prefix: str = "",
) -> Generator[Tuple[str, Any], None, None]:
    for item in urlpatterns:
        if isinstance(item, URLPattern):
            yield prefix + _reformat_pattern(item.pattern), item.callback
        else:
            yield from get_urls(
                item.url_patterns, prefix + _reformat_pattern(item.pattern)
            )


def get_all_urls() -> Generator[Tuple[str, Any], None, None]:
    yield from get_urls(
        __import__(settings.ROOT_URLCONF, {}, {}, [""]).urlpatterns, "/"
    )


def merge_query_dict(query_dict: QueryDict) -> dict:
    return {k: v if len(v) > 1 else v[0] for k, v in query_dict.items() if len(v) > 0}


def is_class_view(handler: Callable) -> bool:
    """
    Judge handler is django.views.View subclass
    """
    return hasattr(handler, "view_class")


class F(partial):
    """
    Python Pipe. e.g.`range(10) | F(filter, lambda x: x % 2) | F(sum)`

    WARNING: There will be a small performance loss when building a
    pipeline. Please do not use it in performance-sensitive locations.
    """

    def __ror__(self, other: Any) -> Any:
        """
        Implement pipeline operators `var | F(...)`
        """
        return self(other)
