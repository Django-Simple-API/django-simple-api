import json
from copy import deepcopy
from typing import Any, Callable, List, Dict, Optional

from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBadRequest

from .functional import bound_params


class SimpleApiMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.JSON = None
        if request.content_type.split(";", 1)[0] == "application/json":
            try:
                request.JSON = json.loads(request.body)
                request.DATA = request.JSON
            except ValueError as ve:
                return HttpResponseBadRequest(
                    "Unable to parse JSON data. Error: {0}".format(ve)
                )
        else:
            if request.method not in ("GET", "POST"):
                # if you want to know why do that,
                # read https://abersheeran.com/articles/Django-Parse-non-POST-Request/
                if hasattr(request, "_post"):
                    del request._post
                    del request._files

                _shadow = request.method
                request.method = "POST"
                request._load_post_and_files()
                request.method = _shadow
            request.DATA = request.POST

        return self.get_response(request)

    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable,
        view_args: List,
        view_kwargs: Dict[str, Any],
    ) -> Optional[HttpResponse]:
        view_func = bound_params(view_func)
        path_params = deepcopy(view_kwargs)
        view_kwargs.clear()
        for name, model in getattr(view_func, "__params__"):
            if name == "path":
                view_kwargs.update(model(**path_params).dict())
            elif name == "query":
                view_kwargs.update(model(**request.GET).dict())
            elif name == "header":
                view_kwargs.update(model(**request.headers).dict())
            elif name == "cookie":
                view_kwargs.update(model(**request.COOKIES).dict())
            elif name == "body":
                view_kwargs.update(model(**request.DATA).dict())
