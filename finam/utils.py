import re
import collections
import six
from operator import attrgetter
from urllib.request import Request

import click

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
    user agent hence setting a custom one
    """
    headers = {'User-Agent': FINAM_TRUSTED_USER_AGENT}
    return Request(url, None, headers)


def parse_script_link(html, src_entry):
    re_src_entry = re.escape(src_entry)
    pattern = '<script src="([^"]*{}[^"]*)"'.format(re_src_entry)
    match = re.search(pattern, html)
    if match is None:
        raise ValueError
    return match.group(1)


def click_validate_enum(enumClass, ctx, param, value):
    if value is not None:
        try:
            enumClass[value]
        except KeyError:
            allowed = map(attrgetter('name'), enumClass)
            raise click.BadParameter('allowed values: {}'
                                     .format(', '.join(allowed)))
    return value
