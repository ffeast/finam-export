import collections
import six

try:
    from urllib2 import Request
except ImportError:
    from urllib.request import Request

from .config import FINAM_CHARSET, FINAM_TRUSTED_USER_AGENT


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


def build_trusted_request(url):
    """
    Builds a request that won't be rejected by finam's protection

    Finam isn't happy to return something for urllib's default
    user agent hence substituting a custom one
    """
    headers = {'User-Agent': FINAM_TRUSTED_USER_AGENT}
    return Request(url, None, headers)

