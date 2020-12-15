import pytest
from django.http.request import QueryDict

from django_simple_api.utils import _merge_query_dict


@pytest.mark.parametrize("query_dict,result", [(QueryDict(mutable=True), {})])
def test_merge_query_dict(query_dict, result):
    assert _merge_query_dict(query_dict) == result
