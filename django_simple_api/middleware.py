import json
from http import HTTPStatus
from typing import Any, Callable, List, Dict, Optional

from django.http.request import HttpRequest
from django.http.response import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
)

from .utils import merge_query_dict
from .exceptions import RequestValidationError


class SimpleApiMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.JSON = None
        if request.content_type == "application/json":
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
                # read https://aber.sh/articles/Django-Parse-non-POST-Request/
                if hasattr(request, "_post"):
                    del request._post
                    del request._files

                _shadow = request.method
                request.method = "POST"
                request._load_post_and_files()
                request.method = _shadow
            request.DATA = merge_query_dict(request.POST)

        return self.get_response(request)

    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable,
        view_args: List[Any],
        view_kwargs: Dict[str, Any],
    ) -> Optional[HttpResponse]:

        # type checking of request parameters
        try:
            # TODO
            # 这里该把 Django 路径参数从 view_args 和 view_kwargs 中摘出来
            pass
        except RequestValidationError as error:
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
    def process_validation_error(
        validation_error: RequestValidationError,
    ) -> HttpResponse:
        return HttpResponse(
            validation_error.json(),
            content_type="application/json",
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
