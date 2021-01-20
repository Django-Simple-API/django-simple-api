import json
from http import HTTPStatus
from typing import Any, Callable, List, Dict, Optional

from django.http.request import HttpRequest
from django.http.response import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
)

from .utils import merge_query_dict, is_view_class
from .exceptions import RequestValidationError
from .params import generate_parameters


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
            view_kwargs.update(generate_parameters(view_func, request, view_kwargs))
        except RequestValidationError as error:
            return self.process_validation_error(error)

        # check the request method of view function
        # class-view does not need to be checked
        if is_view_class(view_func):
            return None

        allow_method = getattr(view_func, "__method__", "")
        if request.method.upper() != allow_method:
            return HttpResponseNotAllowed([allow_method])

        return None  # check completed

    @staticmethod
    def process_validation_error(
        validation_error: RequestValidationError,
    ) -> HttpResponse:
        return HttpResponse(
            validation_error.json(),
            content_type="application/json",
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
