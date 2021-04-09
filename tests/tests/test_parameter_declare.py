import pytest

from django.http import HttpResponse

from pydantic import BaseModel, Field

from django_simple_api import Query
from django_simple_api.exceptions import ExclusiveFieldError
from django_simple_api.params import parse_and_bound_params


class QueryPage(BaseModel):
    size: int = Field(10, alias="page-size")
    num: int = Field(1, alias="page-num")


def test_view_1(request, p1: int = Query(exclusive=True)):
    return HttpResponse()


def test_view_2(request, p1=Query(exclusive=True)):
    return HttpResponse()


def test_view_3(request, p1: QueryPage = Query(exclusive=True), p2: int = Query()):
    return HttpResponse()


def test_view_4(
    request,
    p1: int = Query(),
    p2: QueryPage = Query(exclusive=True),
):
    return HttpResponse()


class TestParameterDeclare:
    def test_parameter_declare_1(self):
        with pytest.raises(TypeError) as e:
            parse_and_bound_params(test_view_1)
        assert (
            str(e.value)
            == "The `p1` parameter of `test_view_1` must use type annotations and "
            "the type annotations must be a subclass of BaseModel."
        )

    def test_parameter_declare_2(self):
        with pytest.raises(TypeError) as e:
            parse_and_bound_params(test_view_2)
        assert (
            str(e.value)
            == "The `p1` parameter of `test_view_2` must use type annotations and "
            "the type annotations must be a subclass of BaseModel."
        )

    def test_parameter_declare_3(self):
        with pytest.raises(ExclusiveFieldError) as e:
            parse_and_bound_params(test_view_3)
        assert (
            str(e.value) == "You used exclusive parameter: `Query(exclusive=True)`, "
            "Please ensure the `Query` field is unique in `test_view_3`."
        )

    def test_parameter_declare_4(self):
        with pytest.raises(ExclusiveFieldError) as e:
            parse_and_bound_params(test_view_4)
        assert (
            str(e.value) == "You used exclusive parameter: `Query(exclusive=True)`, "
            "Please ensure the `Query` field is unique in `test_view_4`."
        )

    def test_parameter_declare_5(self):
        with pytest.raises(ExclusiveFieldError) as e:
            
            def test_view(
                request,
                p1: QueryPage = Query(exclusive=True, title="1"),
            ):
                return HttpResponse()
            
        assert (
            str(e.value)
            == "The `exclusive=True` parameter cannot be used with other parameters at the same time."
        )
