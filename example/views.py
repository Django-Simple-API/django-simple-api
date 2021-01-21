from django.views import View
from django.http.response import HttpResponse

from django_simple_api import Path, Query, Header, Cookie, Body, Exclusive
from django_simple_api.decorators import allow_method


class JustTest(View):
    def get(self, request, id: int = Path(...)):
        return HttpResponse(id)

    def post(self, request, id: int = Path(...), name_id: int = Body(...)):
        return HttpResponse(id + name_id)


@allow_method('get')
def test_get_func(request, name: str = Path(...), name_id: str = Query(...)):
    return HttpResponse(name + name_id)


@allow_method('post')
def test_post_func(request, name: str = Path(...), token: str = Header(..., alias='Authorization')):
    return HttpResponse(name + token)


@allow_method('put')
def test_put_func(request, id: int = Path(1), name: str = Body("2")):
    assert isinstance(id, int), "params type error"
    assert isinstance(name, str), "params type error"
    return HttpResponse(str(id) + name)

