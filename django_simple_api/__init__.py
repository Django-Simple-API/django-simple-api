from .decorators import allow_request_method, describe_response, describe_responses
from .extras import describe_extra_docs
from .fields import Body, Cookie, Exclusive, Header, Path, Query
from .types import UploadFile

__all__ = ["Path", "Query", "Header", "Cookie", "Body", "Exclusive"]
__all__ += ["allow_request_method", "describe_response", "describe_responses"]
__all__ += ["describe_extra_docs"]
__all__ += ["UploadFile"]

default_app_config = "django_simple_api.apps.DjangoSimpleAPIConfig"
