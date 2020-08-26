from django.core.files.base import File

__all__ = ["UploadFile"]


class UploadFile(File):
    """
    Wrapping Django File for `pydantic`
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string", format="binary")

    @classmethod
    def validate(cls, v):
        if not isinstance(v, File):
            raise TypeError("file required")
        return v

    def __repr__(self):
        return f"File({self.name})"
