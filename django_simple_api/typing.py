from typing import Optional, Any

from django.http.request import HttpRequest as _HttpRequest

__all__ = ["HttpRequest"]


class HttpRequest(_HttpRequest):
    JSON: Optional[Any]
    DATA: Optional[Any]
