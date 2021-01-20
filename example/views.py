from django.views import View
from django.http.response import HttpResponse

from django_simple_api import Path, Query, Header, Cookie, Body, Exclusive


class JustTest(View):
    def get(self, request, id: int = Path(...)):
        return HttpResponse(id)
