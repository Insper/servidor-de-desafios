from django.core.exceptions import ValidationError
import json


def json_validator(json_str):
    try:
        json.loads(json_str)
        return json_str
    except e:
        raise ValidationError(
            'String {0} is not a valid JSON string'.format(json_str) + str(e))
