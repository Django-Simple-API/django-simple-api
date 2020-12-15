import typing
import re

from django.conf import settings
from django.urls import URLPattern, URLResolver


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
            # TODO 将 path 转换为 openapi3 标准格式
            yield prefix + str(item.pattern), item.callback
        elif isinstance(item, URLResolver):
            yield from _(item.url_patterns, prefix + str(item.pattern))
        yield from _(lis[1:], prefix)

    yield from _(__import__(settings.ROOT_URLCONF, {}, {}, [""]).urlpatterns)


def _merge_multi_value(raw_list):
    """
    If there are values with the same key value, they are merged into a List.
    """
    d = {}
    for k, v in raw_list:
        if k not in d:
            d[k] = v
            continue
        if isinstance(d[k], list):
            d[k].append(v)
        else:
            d[k] = [d[k], v]
    return d
