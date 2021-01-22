from django.views import View
from django.http.response import HttpResponse
from pydantic import BaseModel, Field

from django_simple_api import Path, Query, Header, Cookie, Body, Exclusive
from django_simple_api.decorators import allow_method


class JustTest(View):
    def get(self, request, id: int = Path(...)):
        return HttpResponse(id)

    def post(self, request, id: int = Path(...), name_id: int = Body(...)):
        return HttpResponse(id + name_id)


@allow_method("get")
def get_func(request, name: str = Path(...), name_id: str = Query(...)):
    return HttpResponse(name + name_id)


@allow_method("post")
def post_func(
    request, name: str = Path(...), token: str = Header(..., alias="Authorization")
):
    return HttpResponse(name + token)


@allow_method("put")
def put_func(request, id: int = Path(1), name: str = Body("2")):
    assert isinstance(id, int), "params type error"
    assert isinstance(name, str), "params type error"
    return HttpResponse(str(id) + name)


@allow_method("get")
def query_page(
    request,
    page_size: int = Query(10, alias="page-size"),
    page_num: int = Query(1, alias="page-num"),
):
    return HttpResponse(page_size * (page_num - 1))


class QueryPage(BaseModel):
    size: int = Field(10, alias="page-size")
    num: int = Field(1, alias="page-num")


@allow_method("get")
def query_page_by_exclusive(request, page: QueryPage = Exclusive("query")):
    return HttpResponse(page.size * (page.num - 1))
