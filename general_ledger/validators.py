from django.core.exceptions import ValidationError


def validate_file_size(value):
    filesize = value.size

    if filesize > 1048576:
        raise ValidationError("You cannot upload file more than 1Mb")
    else:
        return value
