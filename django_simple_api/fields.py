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
