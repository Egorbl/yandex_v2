import json

from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser


class CustomJSONParser(JSONParser):
    """Override the JSONParser parse method. If JSON is not valid, return custom error json"""
    def parse(self, stream, media_type=None, parser_context=None):
        try:
            json_element = super().parse(stream, media_type, parser_context)
            return json_element
        except ParseError:
            return {'code': 400, 'message': 'Validation Failed'}
