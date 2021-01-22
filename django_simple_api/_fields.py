import dataclasses
from typing import Optional

from pydantic.fields import FieldInfo


class PathInfo(FieldInfo):
    pass


class QueryInfo(FieldInfo):
    pass


class HeaderInfo(FieldInfo):
    pass


class CookieInfo(FieldInfo):
    pass


class BodyInfo(FieldInfo):
    pass


@dataclasses.dataclass
class ExclusiveInfo:
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
