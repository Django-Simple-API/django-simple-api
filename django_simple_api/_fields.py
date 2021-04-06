import sys
from typing import Any

if sys.version_info[:2] < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal

from pydantic.fields import FieldInfo as _FieldInfo
from pydantic.fields import Undefined

from .exceptions import ExclusiveFieldError


class FieldInfo(_FieldInfo):
    __slots__ = _FieldInfo.__slots__

    _in: Literal["path", "query", "header", "cookie", "body"]

    def __init__(self, default: Any = Undefined, **kwargs: Any) -> None:
        self.exclusive = kwargs.pop("exclusive")
        if self.exclusive and any(kwargs.values()):
            raise ExclusiveFieldError(
                "The `exclusive=True` parameter cannot be used with other parameters at the same time."
            )
        super().__init__(default, **kwargs)


class PathInfo(FieldInfo):
    __slots__ = ("exclusive", *FieldInfo.__slots__)

    _in: Literal["path"] = "path"


class QueryInfo(FieldInfo):
    __slots__ = ("exclusive", *FieldInfo.__slots__)

    _in: Literal["query"] = "query"


class HeaderInfo(FieldInfo):
    __slots__ = ("exclusive", *FieldInfo.__slots__)

    _in: Literal["header"] = "header"


class CookieInfo(FieldInfo):
    __slots__ = ("exclusive", *FieldInfo.__slots__)

    _in: Literal["cookie"] = "cookie"


class BodyInfo(FieldInfo):
    __slots__ = ("exclusive", *FieldInfo.__slots__)

    _in: Literal["body"] = "body"
