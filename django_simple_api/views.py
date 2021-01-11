from django.shortcuts import render
from django.http.request import HttpRequest
from django.http.response import HttpResponse

from .utils import get_urls


def get_docs(request: HttpRequest):
    for url_pattern, view in get_urls():
        # TODO 完成文档生成
        print(url_pattern, view)
        if hasattr(view, "__methods__"):
            print(view.__methods__)

        if hasattr(view, "__params__"):
            print(view.__params__)

        if hasattr(view, "__responses__"):
            print(view.__responses__)

    return HttpResponse("")


def redoc(request: HttpRequest, template_name: str = "swagger.html"):
    return render(request, template_name, context={})
