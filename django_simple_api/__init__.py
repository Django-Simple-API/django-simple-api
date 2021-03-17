from .decorators import (
    allow_request_method,
    describe_response,
    describe_responses,
    mark_tags,
)
from .extras import describe_extra_docs
from .fields import Body, Cookie, Header, Path, Query
from .types import UploadFile
from .utils import wrapper_include, wrapper_urlpatterns

__all__ = ["Path", "Query", "Header", "Cookie", "Body"]
__all__ += [
    "allow_request_method",
    "describe_response",
    "describe_responses",
    "mark_tags",
]
__all__ += ["describe_extra_docs"]
__all__ += ["UploadFile"]
__all__ += ["wrapper_include", "wrapper_urlpatterns"]

default_app_config = "django_simple_api.apps.DjangoSimpleAPIConfig"
