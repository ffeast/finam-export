from glob import glob
from io import open
import os.path

import urltools

from finam.config import FINAM_CHARSET
from finam.utils import smart_encode


SBER_ID = 3
SBER_CODE = 'SBER'
MICEX_ID = 13851
MICEX_CODE = 'MICEX'
# 10:00 - 18:40
SHARES_SESSION_MINUTES = 60 * 8 + 40


class FixtureRegistry(object):

    """
    Fixtures holder for easier access in tests

    Note it would return bytes in cp1251
    as any reply from finam.ru export tool would do
    """

    __SPLIT_SUFFIX = '__split'

    def __init__(self):
        path = os.path.dirname(os.path.abspath(__file__))
        items = {}
        # glob omits .* so it's used instead of listdir
        for fixture in glob(os.path.join(path, 'fixtures', '*')):
            name, _ = os.path.splitext(os.path.basename(fixture))
            if name in items:
                raise RuntimeError('Duplicate fixture name for {} in {}'
                                   .format(fixture, path))
            with open(fixture, 'r', encoding=FINAM_CHARSET) as f:
                data = f.read()
                items[name] = smart_encode(data)
                items[name + self.__SPLIT_SUFFIX] =\
                    smart_encode(data.split('\n'))
        self._fixtures = items

    def __getattr__(self, key):
        return self._fixtures[key]

fixtures = FixtureRegistry()

# 2.x <-> 3.x compatibility
startswith_compat = type(u'').startswith


def urls_equal(url1, url2):
    return urltools.normalize(url1) == urltools.normalize(url2)
