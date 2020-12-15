from django.http.request import HttpRequest
from django.http.response import HttpResponse

from .utils import get_urls


def get_docs(request: HttpRequest):
    for urlpattern, view in get_urls():
        print(urlpattern, view)
    return HttpResponse("")


def redoc(request: HttpRequest):
    return HttpResponse("")
