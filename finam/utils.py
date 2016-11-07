import collections
import six

from .config import FINAM_CHARSET


def is_container(val):
    return isinstance(val, collections.Container)\
             and not isinstance(val, six.string_types) \
             and not isinstance(val, bytes)


def smart_encode(val, charset=FINAM_CHARSET):
    if is_container(val):
        return [v.encode(charset) for v in val]
    return val.encode(charset)


def smart_decode(val, charset=FINAM_CHARSET):
    if is_container(val):
        return [v.decode(charset) for v in val]
    return val.decode(charset)

