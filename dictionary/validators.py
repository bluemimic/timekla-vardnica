from django.forms import ValidationError
from django.utils.deconstruct import deconstructible
import csv


@deconstructible
class FileSizeValidator:
    message = "File size “%(size)d” is not allowed. File size must be under %(max_size)d."
    code = "invalid_file_size"

    def __init__(self, max_size: int = 2_500_000, message=None, code=None):
        self.max_size = max_size
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        file_size = value.size
        if file_size > self.max_size:
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    "size": file_size,
                    "max_size": self.max_size,
                    "value": value,
                },
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.max_size == other.max_size
            and self.message == other.message
            and self.code == other.code
        )


@deconstructible
class CSVFileValidator:
    message = "This is invalit .csv file"
    code = "invalid_csv_file"

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        if value.multiple_chunks():
            for chunk in value.chunks():
                value.read(chunk)
        else:
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    "value": value,
                },
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.message == other.message
            and self.code == other.code
        )
