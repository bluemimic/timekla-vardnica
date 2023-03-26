from django.core.files.uploadedfile import UploadedFile

def has_file_correct_extension(file: UploadedFile, extension: str) -> bool:
    """
    This function returns True if an extension provided corresponds with the file's extension,
    False otherwise.
    """

    return file.name.split('.')[-1] == extension


def has_file_correct_size(file: UploadedFile, size: int = 2_500_000) -> bool:
    """
    This function returns True if the file's size is less than `size` provided,
    False otherwise.
    """

    return file.size < size


# def is_csv_file_valid(file: UploadedFile) -> bool:
    