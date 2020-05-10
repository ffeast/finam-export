# coding: utf-8
import datetime
import logging
import operator
from enum import IntEnum
from io import StringIO

try:
    from urllib import urlencode
    from urllib2 import urlopen
except ImportError:
    from urllib.parse import urlencode
    from urllib.request import urlopen

import pandas as pd
from pandas.io.parsers import ParserError

from finam.utils import (is_container,
                         smart_decode,
                         build_trusted_request,
                         parse_script_link)

__all__ = ['Market',
           'Timeframe',
           'FinamExportError',
           'FinamDownloadError',
           'FinamParsingError',
           'FinamTooLongTimeframeError',
           'FinamObjectNotFoundError',
           'Exporter']


logger = logging.getLogger(__name__)


class Market(IntEnum):

    """
    Markets mapped to ids used by finam.ru export

    List is incomplete, extend it when needed
    """

    BONDS = 2
    COMMODITIES = 24
    CURRENCIES_WORLD = 5
    CURRENCIES = 45
    ETF = 28
    ETF_MOEX = 515
    FUTURES = 14  # non-expired futures
    FUTURES_ARCHIVE = 17  # expired futures
    FUTURES_USA = 7
    INDEXES = 6
    SHARES = 1
    SPB = 517
    USA = 25


class Timeframe(IntEnum):

    TICKS = 1
    MINUTES1 = 2
    MINUTES5 = 3
    MINUTES10 = 4
    MINUTES15 = 5
    MINUTES30 = 6
    HOURLY = 7
    DAILY = 8
    WEEKLY = 9
    MONTHLY = 10


class LookupComparator(IntEnum):

    EQUALS = 1
    STARTSWITH = 2
    CONTAINS = 3


class FinamExportError(Exception):
    pass


class FinamDownloadError(FinamExportError):
    pass


class FinamThrottlingError(FinamExportError):
    pass


class FinamParsingError(FinamExportError):
    pass


class FinamObjectNotFoundError(FinamExportError):
    pass


class FinamTooLongTimeframeError(FinamExportError):
    pass


def fetch_url(url, lines=False):
    """
    Fetches url from finam.ru
    """
    logger.info('Fetching {}'.format(url))
    request = build_trusted_request(url)
    try:
        fh = urlopen(request)
        if lines:
            response = fh.readlines()
        else:
            response = fh.read()
    except IOError as e:
        raise FinamDownloadError('Unable to load {}: {}'.format(url, e))
    try:
        return smart_decode(response)
    except UnicodeDecodeError as e:
        raise FinamDownloadError('Unable to decode: {}'.format(e.message))


class ExporterMetaPage(object):

    FINAM_BASE = 'https://www.finam.ru'
    FINAM_ENTRY_URL = FINAM_BASE + '/profile/moex-akcii/gazprom/export/'
    FINAM_META_FILENAME = 'icharts.js'

    def __init__(self, fetcher=fetch_url):
        self._fetcher = fetcher

    def find_meta_file(self):
        """
        Finds finam's meta dictionary path

        From 03.2019 onwards it moved to a temporary path, from its url
        it looks like a transient cache and needs to be discovered every time

        Included as
        <script src="/somepath/icharts.js" type="text/javascript"></script>
        into raw HTML page code
        """
        html = self._fetcher(self.FINAM_ENTRY_URL)
        try:
            url = parse_script_link(html, self.FINAM_META_FILENAME)
        except ValueError as e:
            raise FinamParsingError('Unable to parse meta url from html: {}'
                                    .format(e))
        return self.FINAM_BASE + url


class ExporterMetaFile(object):

    FINAM_CATEGORIES = -1

    def __init__(self, url, fetcher=fetch_url):
        self._url = url
        self._fetcher = fetcher

    def _parse_js_assignment(self, line):
        """
        Parses 1-line js assignment used by finam.ru

        Can be either (watch spaces between commas)
        var string_arr = ['string1','string2',...,'stringN'] or
        var ints_arr = [int1,...,intN]

        May also contain empty strings ['abc','','']
        """
        logger.debug('Parsing line starting with "{}"'.format(line[:20]))

        # extracting everything between array brackets
        start_char, end_char = '[', ']'
        start_idx = line.find(start_char)
        end_idx = line.find(end_char)
        if (start_idx == -1 or
                end_idx == -1):
            raise FinamDownloadError('Unable to parse line: {}'.format(line))
        items = line[start_idx + 1:end_idx]

        # string items
        if items.startswith("'"):
            # it may contain ',' inside lines so cant split by ','
            # i.e. "GILEAD SCIENCES, INC."
            items = items.split("','")
            for i in (0, -1):
                items[i] = items[i].strip("'")
            return items

        # int items
        return items.split(',')

    def _parse_js(self, data):
        """
        Parses js file used by finam.ru export tool
        """
        cols = ('id', 'name', 'code', 'market')
        parsed = dict()
        for idx, col in enumerate(cols[:len(cols)]):
            parsed[col] = self._parse_js_assignment(data[idx])
        df = pd.DataFrame(columns=cols, data=parsed)
        df['market'] = df['market'].astype(int)
        # junk data + non-int ids, we don't need it
        df = df[df.market != self.FINAM_CATEGORIES]
        # now we can coerce ids to ints
        df['id'] = df['id'].astype(int)
        df.set_index('id', inplace=True)
        df.sort_values('market', inplace=True)
        return df

    def parse_df(self):
        response = self._fetcher(self._url, lines=True)
        return self._parse_js(response)


class ExporterMeta(object):

    def __init__(self, lazy=True, fetcher=fetch_url):
        self._meta = None
        self._fetcher = fetcher
        if not lazy:
            self._load()

    def _load(self):
        if self._meta is not None:
            return self._meta
        page = ExporterMetaPage(self._fetcher)
        meta_url = page.find_meta_file()
        meta_file = ExporterMetaFile(meta_url, self._fetcher)
        self._meta = meta_file.parse_df()

    @property
    def meta(self):
        return self._meta.copy(deep=True)

    def _apply_filter(self, col, val, comparator):
        """
        Builds a dataframe matching original dataframe with conditions passed

        The original dataframe is left intact
        """
        if not is_container(val):
            val = [val]

        if comparator == LookupComparator.EQUALS:
            # index must be sliced differently
            if col == 'id':
                expr = self._meta.index.isin(val)
            else:
                expr = self._meta[col].isin(val)
        else:
            if comparator == LookupComparator.STARTSWITH:
                op = 'startswith'
            else:
                op = 'contains'
            expr = self._combine_filters(
                map(getattr(self._meta[col].str, op), val), operator.or_)
        return expr

    def _combine_filters(self, filters, op):
        itr = iter(filters)
        result = next(itr)
        for filter_ in itr:
            result = op(result, filter_)
        return result

    def lookup(self, id_=None, code=None, name=None, market=None,
               name_comparator=LookupComparator.CONTAINS,
               code_comparator=LookupComparator.EQUALS):
        """
        Looks up contracts matching specified combinations of requirements
        If multiple requirements are specified they will be ANDed

        Note that the same id can have multiple matches as an entry
        may appear in different markets
        """
        if not any((id_, code, name, market)):
            raise ValueError('Either id or code or name or market'
                             ' must be specified')

        self._load()
        filters = []

        # applying filters
        filter_groups = (('id', id_, LookupComparator.EQUALS),
                         ('code', code, code_comparator),
                         ('name', name, name_comparator),
                         ('market', market, LookupComparator.EQUALS))

        for col, val, comparator in filter_groups:
            if val is not None:
                filters.append(self._apply_filter(col, val, comparator))

        combined_filter = self._combine_filters(filters, operator.and_)
        res = self._meta[combined_filter]
        if len(res) == 0:
            raise FinamObjectNotFoundError
        return res


class Exporter(object):

    DEFAULT_EXPORT_HOST = 'export.finam.ru'
    IMMUTABLE_PARAMS = {
        'd': 'd',
        'f': 'table',
        'e': '.csv',
        'dtf': '1',
        'tmf': '3',
        'MSOR': '0',
        'mstime': 'on',
        'mstimever': '1',
        'sep': '3',
        'sep2': '1',
        'at': '1'
    }

    ERROR_TOO_MUCH_WANTED = (u'Вы запросили данные за слишком '
                             u'большой временной период')

    ERROR_THROTTLING = 'Forbidden: Access is denied'

    def __init__(self, export_host=None, fetcher=fetch_url):
        self._meta = ExporterMeta(lazy=True)
        self._fetcher = fetcher
        if export_host is not None:
            self._export_host = export_host
        else:
            self._export_host = self.DEFAULT_EXPORT_HOST

    def _build_url(self, params):
        url = ('http://{}/table.csv?{}&{}'
               .format(self._export_host,
                       urlencode(self.IMMUTABLE_PARAMS),
                       urlencode(params)))
        return url

    def _sanity_check(self, data):
        if self.ERROR_TOO_MUCH_WANTED in data:
            raise FinamTooLongTimeframeError

        if self.ERROR_THROTTLING in data:
            raise FinamThrottlingError

        if not all(c in data for c in '<>;'):
            raise FinamParsingError('Returned data doesnt seem like '
                                    'a valid csv dataset: {}'.format(data))

    def lookup(self, *args, **kwargs):
        return self._meta.lookup(*args, **kwargs)

    def download(self,
                 id_,
                 market,
                 start_date=datetime.date(2007, 1, 1),
                 end_date=None,
                 timeframe=Timeframe.DAILY):

        items = self._meta.lookup(id_=id_, market=market)
        # i.e. for markets 91, 519, 2
        # id duplicates are feasible, looks like corrupt data on finam
        # can do nothing about it but inform the user
        if len(items) != 1:
            raise FinamDownloadError('Duplicate items for id={} on market {}'
                                     .format(id_, market))
        code = items.iloc[0]['code']

        if end_date is None:
            end_date = datetime.date.today()

        params = {
            'p': timeframe.value,
            'em': id_,
            'market': market.value,
            'df': start_date.day,
            'mf': start_date.month - 1,
            'yf': start_date.year,
            'dt': end_date.day,
            'mt': end_date.month - 1,
            'yt': end_date.year,
            'cn': code,
            'code': code,
            # I would guess this param denotes 'data format'
            # that differs for ticks only
            'datf': 6 if timeframe == Timeframe.TICKS.value else 5
        }

        url = self._build_url(params)
        # deliberately not using pd.read_csv's ability to fetch
        # urls to fully control what's happening
        data = self._fetcher(url)
        self._sanity_check(data)
        if timeframe == Timeframe.TICKS:
            date_cols = [2, 3]
        else:
            date_cols = [0, 1]

        try:
            df = pd.read_csv(StringIO(data),
                             index_col=0,
                             parse_dates={'index': date_cols},
                             sep=';')
            df.sort_index(inplace=True)
        except ParserError as e:
            raise FinamParsingError(e.message)

        return df
