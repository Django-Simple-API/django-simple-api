import re
import typing

from django.conf import settings
from django.urls import URLPattern, URLResolver
from django.http.request import QueryDict

CONVERT_REG = [
    r"\^?([a-zA-Z0-9_]+)\$?",  # /articles
    r"\^?<([a-zA-Z0-9_]+)>\$?",  # /<name>
    r"\^?<[a-zA-Z]+:([a-zA-Z0-9_]+)>\$?",  # /<int:id>
    r"\^?\(\?P<(.*?)>.*?\)\$?",  # '^(?P<app_label>auth)'
]


def convert_url(url_pattern: URLPattern) -> typing.Generator[str, None, None]:
    path_list: typing.List[str] = str(url_pattern.pattern).split("/")
    for path in path_list:
        if path in ["", "$"]:
            yield ""
            continue
        for idx, reg in enumerate(CONVERT_REG):
            match_res = re.match(reg, path)
            if match_res is None:
                continue
            if idx == 0:
                yield match_res.group(1)
            else:
                yield "{%s}" % match_res.group(1)
            break
        else:
            yield path


def get_urls() -> typing.Generator[typing.Tuple[str, typing.Any], None, None]:
    def _(
        lis, prefix: str = ""
    ) -> typing.Generator[typing.Tuple[str, typing.Any], None, None]:
        """
        return urlpatterns and view function
        """
        if not lis:
            return
        item = lis[0]
        if isinstance(item, URLPattern):
            # 将 path 转换为 openapi3 标准格式
            print("---contrast: " + prefix + str(item.pattern))
            yield prefix + "/".join(convert_url(item)), item.callback
        elif isinstance(item, URLResolver):
            yield from _(item.url_patterns, prefix + str(item.pattern))
        yield from _(lis[1:], prefix)

    yield from _(__import__(settings.ROOT_URLCONF, {}, {}, [""]).urlpatterns)


def _merge_query_dict(query_dict: QueryDict) -> dict:
    return {k: v if len(v) > 1 else v[0] for k, v in query_dict.items() if len(v) > 0}
