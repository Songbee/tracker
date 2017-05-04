import codecs
from base64 import b32decode, b16encode

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