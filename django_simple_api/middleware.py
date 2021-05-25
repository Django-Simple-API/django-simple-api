import json
from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional

from django.http.request import HttpRequest
from django.http.response import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
)
from django.utils.deprecation import MiddlewareMixin

from .exceptions import RequestValidationError
from .params import verify_params
from .utils import merge_query_dict


class ParseRequestDataMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest) -> HttpResponse:
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
            request.DATA = dict(
                **merge_query_dict(request.POST), **merge_query_dict(request.FILES)
            )


class ValidateRequestDataMiddleware(ParseRequestDataMiddleware):
    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable,
        view_args: List[Any],
        view_kwargs: Dict[str, Any],
    ) -> Optional[HttpResponse]:

        # Put request method check before request parameters check.
        if hasattr(view_func, "__method__") and not (
            getattr(view_func, "__method__", None) == request.method.upper()
        ):
            return HttpResponseNotAllowed([view_func.__method__])  # type: ignore

        try:
            view_kwargs.update(verify_params(view_func, request, view_kwargs))
            return None
        except RequestValidationError as error:
            return self.process_validation_error(error)

    @staticmethod
    def process_validation_error(
        validation_error: RequestValidationError,
    ) -> HttpResponse:
        return HttpResponse(
            validation_error.json(),
            content_type="application/json",
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
        )


class SimpleApiMiddleware(ValidateRequestDataMiddleware):
    """
    Contains all the functional middleware of Django Simple API. More
    functions may be added to this middleware at any time. If you only
    need certain functions, please use other middleware explicitly.
    """
