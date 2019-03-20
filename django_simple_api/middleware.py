import json

from django.http import HttpResponseBadRequest
from django.utils.deprecation import MiddlewareMixin


class RequestParsingMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.JSON = None
        if request.content_type != "application/json":
            if request.method not in ("GET", "POST"):
                # if you want to know why do that,
                # read https://abersheeran.com/articles/Django-Parse-non-POST-Request/
                if hasattr(request, '_post'):
                    del request._post
                    del request._files

                _shadow = request.method
                request.method = "POST"
                request._load_post_and_files()
                request.method = _shadow
            request.DATA = request.POST
        else:
            try:
                request.JSON = json.loads(request.body)
                request.DATA = request.JSON
            except ValueError as ve:
                return HttpResponseBadRequest("Unable to parse JSON data. Error: {0}".format(ve))
