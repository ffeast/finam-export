from glob import glob
import os.path


SBER_ID = 3
SBER_CODE = 'SBER'
MICEX_ID = 13851
MICEX_CODE = 'MICEX'
# 10:00 - 18:40
SHARES_SESSION_MINUTES = 60 * 8 + 40


class FixtureRegistry(object):

    """
    Fixtures holder for easier access in tests
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
            with open(fixture, 'r') as f:
                items[name] = f.read()
        self._fixtures = items

    def __getattr__(self, key):
        if key.endswith(self.__SPLIT_SUFFIX):
            real_key = key[:-len(self.__SPLIT_SUFFIX)]
            return self._fixtures[real_key].split('\n')
        return self._fixtures[key]

fixtures = FixtureRegistry()
