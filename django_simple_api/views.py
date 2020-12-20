from django.http.request import HttpRequest
from django.http.response import HttpResponse

from .utils import get_urls
from .functional import bound_params


def get_docs(request: HttpRequest):
    for urlpattern, view in get_urls():
        # TODO 完成文档生成
        print(urlpattern, view)
        getattr(bound_params(view), "__params__")
    return HttpResponse("")


def redoc(request: HttpRequest):
    return HttpResponse("")
