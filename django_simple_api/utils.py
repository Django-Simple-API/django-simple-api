import re
from types import MethodType
from inspect import signature
from typing import TypeVar, Callable, Any, Awaitable, List, Union, Generator, Tuple

from pydantic import create_model

from django.conf import settings
from django.urls import URLPattern, URLResolver
from django.urls.conf import RoutePattern, RegexPattern
from django.http.request import QueryDict

from .fields import PathInfo, QueryInfo, HeaderInfo, CookieInfo, BodyInfo

T = TypeVar("T", Callable[..., Any], Callable[..., Awaitable[Any]])

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


RouteGenerator = Generator[Tuple[str, Any], None, None]


def get_urls() -> RouteGenerator:
    def _(
        urlpatterns: List[Union[URLPattern, URLResolver]],
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


def bind_params(view_func: T) -> T:
    if hasattr(view_func, "__params__"):
        return view_func

    def bind(real_func: T):

        func: T
        if isinstance(real_func, MethodType):
            func = real_func.__func__
        else:
            func = real_func

        sig = signature(func)
        __params__ = {}
        path, query, header, cookie, body, other = {}, {}, {}, {}, {}, {}  # type: ignore

        for name, param in sig.parameters.items():
            # 忽略部分参数
            if name in ("self", "request", "args", "kwargs", "*args", "**kwargs"):
                continue

            default = param.default
            annotation = param.annotation

            if isinstance(default, QueryInfo):
                _type_ = query
            elif isinstance(default, HeaderInfo):
                _type_ = header
            elif isinstance(default, CookieInfo):
                _type_ = cookie
            elif isinstance(default, BodyInfo):
                _type_ = body
            elif isinstance(default, PathInfo):
                _type_ = path
            else:
                # 未标注类型的参数会被丢弃
                _type_ = other

            if annotation != param.empty:
                if default == param.empty:
                    _type_[name] = (annotation, ...)
                else:
                    _type_[name] = (annotation, default)
            elif default != param.empty:
                _type_[name] = default

        for key in ("path", "query", "header", "cookie", "body"):
            if locals()[key]:
                __params__[key] = create_model(f"temporary_{key}", **locals()[key])

        setattr(func, "__params__", __params__)
        return func

    if hasattr(view_func, "view_class"):
        view_class = view_func.view_class  # type: ignore
        allow_methods = view_class.http_method_names

        funcs = [getattr(view_class, method) for method in allow_methods if hasattr(view_class, method)]  # type: ignore

        for cls_func in funcs:
            bind(cls_func)

        setattr(view_func, "__params__", {})
        return view_func
    else:
        bind(view_func)
    return view_func


def _merge_query_dict(query_dict: QueryDict) -> dict:
    return {k: v if len(v) > 1 else v[0] for k, v in query_dict.items() if len(v) > 0}
