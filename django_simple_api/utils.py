import re
from typing import Any, List, Union, Generator, Tuple, Callable

from django.conf import settings
from django.urls import URLPattern, URLResolver
from django.urls.conf import RoutePattern, RegexPattern
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


def get_urls() -> Generator[Tuple[str, Any], None, None]:
    def _(
        urlpatterns: List[Union[URLPattern, URLResolver]],
        prefix: str = "",
    ) -> Generator[Tuple[str, Any], None, None]:
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


def merge_query_dict(query_dict: QueryDict) -> dict:
    return {k: v if len(v) > 1 else v[0] for k, v in query_dict.items() if len(v) > 0}


def is_class_view(handler: Callable) -> bool:
    """
    Judge handler is django.views.View subclass
    """
    return hasattr(handler, "view_class")


def parse_function_doc(function: Callable) -> tuple:
    """
    Parse and return function doc.
    """
    doc = function.__doc__
    if doc is None:
        return "", ""
    docs = doc.split("\n\n", maxsplit=1)
    summary = docs[0].strip().replace("\n", "").replace("    ", " ")
    if len(docs) == 1:
        description = ""
    else:
        description = docs[-1].strip().replace("\n", "").replace("    ", " ")
    return summary, description


def parse_function_params(method: str, function: Callable) -> Tuple[list, dict]:
    """
    Parse and return function params.
    """
    params = getattr(function, "__parameters__", None)
    body = getattr(function, "__request_body__", None)
    params_info = []
    body_info = {}
    if params:
        for typ, model in params.items():
            for name, field in model.__fields__.items():
                param_info = {
                    "in": typ,
                    "name": name,
                    "description": field.description if hasattr(field, "description") else "",
                    "required": field.required,
                    "schema": {"type": field.type_.__name__},
                }
                for item in ["alias", "default", "const", "gt", "ge", "lt", "le", "multiple_of", "min_items",
                             "max_items", "min_length", "max_length", "regex"]:
                    if hasattr(field, "item"):
                        param_info["schema"][item] = getattr(field, item, None)
                params_info.append(param_info)
        print(params_info)

    # todo 未完成
    if body:
        pass
    return params_info, body_info
