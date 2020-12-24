import pytest
from django.http.request import QueryDict
from django.urls import path, re_path

from django_simple_api.utils import _merge_query_dict, _reformat_pattern


@pytest.mark.parametrize("query_dict,result", [(QueryDict(mutable=True), {})])
def test_merge_query_dict(query_dict, result):
    assert _merge_query_dict(query_dict) == result


@pytest.mark.parametrize(
    "pattern,path_format",
    [
        (path("", lambda request: None).pattern, ""),
        (path("<user>", lambda request: None).pattern, "{user}"),
        (path("<str:user>", lambda request: None).pattern, "{user}"),
        (re_path(r"^(?P<user>.*?)$", lambda request: None).pattern, "{user}"),
    ],
)
def test_reformat_pattern(pattern, path_format):
    assert _reformat_pattern(pattern) == path_format
