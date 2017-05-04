from base64 import b32decode, b16encode

from flask import url_for
from flask.views import MethodView


def external_url_for(endpoint, **values):
    return url_for(endpoint, _external=True, **values)


def b32_to_b16(s):
    return b16encode(b32decode(s.upper()))


def flatten(x):
    """
    http://stackoverflow.com/a/406822/1593459
    """
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, str):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result


class APIMethodView(MethodView):
    """
    Enable browsable APIs for views with no GET handler.
    """

    def get(self):
        return {"error": "Method not allowed"}, 400
