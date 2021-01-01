import json
from http import HTTPStatus
from typing import Any, Callable, List, Dict, Optional

from pydantic import ValidationError
from django.http.request import HttpRequest
from django.http.response import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
)

from .utils import bind_params, _merge_query_dict


class SimpleApiMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.JSON = None
        if request.content_type.split(";", 1)[0] == "application/json":
            try:
                request.JSON = json.loads(request.body)
            except ValueError as ve:
                return HttpResponseBadRequest(
                    "Unable to parse JSON data. Error: {0}".format(ve)
                )
            request.DATA = request.JSON
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
            request.DATA = _merge_query_dict(request.POST)

        return self.get_response(request)

    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable,
        view_args: List[Any],
        view_kwargs: Dict[str, Any],
    ) -> Optional[HttpResponse]:
        view_func = bind_params(view_func)

        # type checking of request parameters
        try:
            for name, model in getattr(view_func, "__params__").items():
                if name == "path":
                    view_kwargs.update(model(**view_kwargs).dict())
                elif name == "query":
                    view_kwargs.update(model(**_merge_query_dict(request.GET)).dict())
                elif name == "header":
                    view_kwargs.update(model(**request.headers).dict())
                elif name == "cookie":
                    view_kwargs.update(model(**request.COOKIES).dict())
                elif name == "body":
                    view_kwargs.update(model(**request.DATA).dict())
        except ValidationError as error:
            return self.process_validation_error(error)

        # check the request method of view function
        # class-view does not need to be checked
        if hasattr(view_func, "view_class"):
            return None

        allow_methods = getattr(view_func, "__methods__", [])
        if request.method.upper() not in allow_methods:
            return HttpResponseNotAllowed(allow_methods)

        # check completed
        return None

    @staticmethod
    def process_validation_error(validation_error: ValidationError) -> HttpResponse:
        return HttpResponse(
            validation_error.json(),
            content_type="application/json",
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
