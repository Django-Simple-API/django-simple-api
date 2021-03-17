from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views import View
from pydantic import BaseModel, Field

from django_simple_api import Body, Cookie, Header, Path, Query, allow_request_method


class JustTest(View):
    def get(
        self,
        request: HttpRequest,
        id: int = Path(..., description="This is description of id."),
    ) -> HttpResponse:
        """
        This is summary.

        This is description.
        """
        return HttpResponse(id)

    def post(self, request, id: int = Path(...), name_id: int = Body(...)):
        return HttpResponse(id + name_id)


@allow_request_method("get")
def get_func(request, name: str = Path(...), name_id: str = Query(...)):
    return HttpResponse(name + name_id)


@allow_request_method("post")
def post_func(
    request, name: str = Path(...), token: str = Header(..., alias="Authorization")
):
    return HttpResponse(name + token)


@allow_request_method("put")
def put_func(request, id: int = Path(1), name: str = Body("2")):
    assert isinstance(id, int), "params type error"
    assert isinstance(name, str), "params type error"
    return HttpResponse(str(id) + name)


@allow_request_method("delete")
def test_delete_func(request, id: int = Path(...), session_id: str = Cookie(...)):
    return HttpResponse(str(id) + session_id)


@allow_request_method("get")
def query_page(
    request,
    page_size: int = Query(10, alias="page-size"),
    page_num: int = Query(1, alias="page-num"),
):
    return HttpResponse(page_size * (page_num - 1))


class QueryPage(BaseModel):
    size: int = Field(10, alias="page-size")
    num: int = Field(1, alias="page-num")


@allow_request_method("get")
def query_page_by_exclusive(request, page: QueryPage = Query(exclusive=True)):
    return HttpResponse(page.size * (page.num - 1))


def test_common_func_view(request):
    id = request.GET.get("id", "")
    name = request.POST.get("name", "")
    return HttpResponse(id + name)


def test_common_path_func_view(request, id):
    name = request.GET.get("name", "")
    return HttpResponse(id + name)


class CommonClassView(View):
    def get(self, request):
        id = request.GET.get("id", "")
        return HttpResponse(id)

    def post(self, request):
        name = request.POST.get("name", "")
        return HttpResponse(name)
