import typing

from django.conf import settings
from django.urls import URLPattern, URLResolver
from django.http.request import QueryDict


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


def _merge_query_dict(query_dict: QueryDict) -> dict:
    return {k: v if len(v) > 1 else v[0] for k, v in query_dict.items() if len(v) > 0}
