import re

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


def validate_image_sizes_json(sizes):
    validator_format = r'^[\w\-\.]+ \d+w$'
    url_validator = URLValidator()

    if not sizes:
        return

    for size in sizes:
        (source, image_size) = size.split(" ")

        # Validate that the source is a valid URL
        url_validator(source)

        # Get the file name with its size
        image_with_size = size.split("/")[-1]

        if not re.search(validator_format, image_with_size):
            raise ValidationError(
                "'%(size)s' size doesn't match the required format %(format)s", params={'format': validator_format, 'size': image_with_size})
