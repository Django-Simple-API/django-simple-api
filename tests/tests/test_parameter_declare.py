from django.http import HttpResponse

from pydantic import BaseModel, Field

from django_simple_api import Query
from django_simple_api.exceptions import ExclusiveFieldError
from django_simple_api.params import parse_and_bound_params


class QueryPage(BaseModel):
    size: int = Field(10, alias="page-size")
    num: int = Field(1, alias="page-num")


def just_view_1(request, p1: int = Query(exclusive=True)):
    return HttpResponse()


def just_view_2(request, p1=Query(exclusive=True)):
    return HttpResponse()


def just_view_3(request, p1: QueryPage = Query(exclusive=True), p2: int = Query()):
    return HttpResponse()


def just_view_4(
    request,
    p1: int = Query(),
    p2: QueryPage = Query(exclusive=True),
):
    return HttpResponse()


def just_view_5(
    request,
    p1: QueryPage = Query(exclusive=True, default="1"),
):
    return HttpResponse()


class TestParameterDeclare:
    def test_parameter_declare_1(self):
        try:
            parse_and_bound_params(just_view_1)
        except TypeError as e:
            assert (
                str(e)
                == "The `p1` parameter of `just_view_1` must use type annotations and "
                "the type annotations must be a subclass of BaseModel."
            )

    def test_parameter_declare_2(self):
        try:
            parse_and_bound_params(just_view_2)
        except TypeError as e:
            assert (
                str(e)
                == "The `p1` parameter of `just_view_2` must use type annotations and "
                "the type annotations must be a subclass of BaseModel."
            )

    def test_parameter_declare_3(self):
        try:
            parse_and_bound_params(just_view_3)
        except ExclusiveFieldError as e:
            assert (
                str(e) == "You used exclusive parameter: `Query(exclusive=True)`, "
                "Please ensure the `Query` field is unique in `just_view_3`."
            )

    def test_parameter_declare_4(self):
        try:
            parse_and_bound_params(just_view_4)
        except ExclusiveFieldError as e:
            assert (
                str(e) == "You used exclusive parameter: `Query(exclusive=True)`, "
                "Please ensure the `Query` field is unique in `just_view_4`."
            )

    def test_parameter_declare_5(self):
        try:
            parse_and_bound_params(just_view_5)
        except ExclusiveFieldError as e:
            assert (
                str(e)
                == "The `exclusive=True` parameter cannot be used with other parameters at the same time."
            )
