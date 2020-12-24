import re
import typing

from django.conf import settings
from django.urls import URLPattern, URLResolver
from django.urls.conf import RoutePattern, RegexPattern
from django.http.request import QueryDict

RE_PATH_PATTERN = re.compile(r"\(\?P<(?P<name>\w*)>.*?\)")
PATH_PATTERN = re.compile(r"<(.*?:)?(?P<name>\w*)>")
REPLACE_RE_FLAG_PATTERN = re.compile(r"(?<!\\)\^|(?<!\\)\$")


def _reformat_pattern(pattern: typing.Union[RoutePattern, RegexPattern]) -> str:
    path_format = str(pattern)
    if isinstance(pattern, RoutePattern):
        pattern = PATH_PATTERN
    else:  # RegexPattern
        path_format = re.sub(REPLACE_RE_FLAG_PATTERN, "", path_format)
        pattern = RE_PATH_PATTERN
    return re.sub(pattern, r"{\g<name>}", path_format)


RouteGenerator = typing.Generator[typing.Tuple[str, typing.Any], None, None]


def get_urls() -> RouteGenerator:
    def _(
        urlpatterns: typing.List[typing.Union[URLPattern, URLResolver]],
        prefix: str = "",
    ) -> RouteGenerator:
        """
        return urlpatterns and view function
        """
        for item in urlpatterns:
            if isinstance(item, URLPattern):
                yield prefix + _reformat_pattern(item.pattern), item.callback
            else:
                yield from _(
                    item.url_patterns, prefix + _reformat_pattern(item.pattern)
                )

    yield from _(__import__(settings.ROOT_URLCONF, {}, {}, [""]).urlpatterns)


def _merge_query_dict(query_dict: QueryDict) -> dict:
    return {k: v if len(v) > 1 else v[0] for k, v in query_dict.items() if len(v) > 0}
