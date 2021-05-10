from io import BytesIO

from django.core.files.base import File

__all__ = ["UploadFile", "UploadImage"]


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


class UploadImage(UploadFile):
    @classmethod
    def validate(cls, v):
        v = super().validate(v)

        from PIL import Image

        # We need to get a file object for Pillow. We might have a path or we might
        # have to read the data into memory.
        if hasattr(v, "temporary_file_path"):
            file = v.temporary_file_path()
        else:
            file = BytesIO(v.read())
        try:
            # load() could spot a truncated JPEG, but it loads the entire
            # image in memory, which is a DoS vector. See #3848 and #18520.
            image = Image.open(file)
            # verify() must be called immediately after the constructor.
            image.verify()

            # Annotating so subclasses can reuse it for their own validation
            v.image = image
            # Pillow doesn't detect the MIME type of all formats. In those
            # cases, content_type will be None.
            v.content_type = Image.MIME.get(image.format)
        except Exception:
            # Pillow doesn't recognize it as an image.
            raise TypeError(
                "Upload a valid image. The file you uploaded "
                "was either not an image or a corrupted image."
            )
        if hasattr(v, "seek") and callable(v.seek):
            v.seek(0)
        return v

    def __repr__(self):
        return f"Image({self.name})"
