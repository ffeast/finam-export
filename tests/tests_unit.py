import operator
from datetime import date

import mock
import pandas as pd
from nose.tools import assert_raises, assert_raises_regexp
from parameterized import parameterized

from finam import (Market,
                   Timeframe,
                   LookupComparator,
                   FinamDownloadError,
                   FinamParsingError,
                   FinamObjectNotFoundError)
from finam.export import (ExporterMeta,
                          ExporterMetaPage,
                          ExporterMetaFile)
from finam.interval import split_interval

from . import fixtures, startswith_compat, SBER, MICEX


class TestExporterMetaPage(object):

    def test_find_ok(self):
        fetcher = mock.MagicMock(return_value=fixtures.page_valid)
        actual = ExporterMetaPage(fetcher).find_meta_file()
        expected = 'https://www.finam.ru/cache/N72Hgd54/icharts/icharts.js'
        assert expected == actual

    def test_find_on_broken_page(self):
        fetcher = mock.MagicMock(return_value=fixtures.page_broken)
        with assert_raises(FinamParsingError):
            ExporterMetaPage(fetcher).find_meta_file()


class TestExporterMetaFile(object):

    def test_parse_df_ok(self):
        fetcher = mock.MagicMock(return_value=fixtures.meta_valid__split)
        meta_file = ExporterMetaFile('https://example.com', fetcher)
        actual = meta_file.parse_df()

        assert isinstance(actual, pd.DataFrame)
        assert actual.columns.tolist() == ['name', 'code', 'market']
        assert len(actual['market'].unique()) == 32
        assert len(actual) > len(actual['market'].unique())

        sber = actual[(actual['code'] == SBER.code)
                      & (actual['market'] == Market.SHARES)]
        assert sber['name'].values[0] == u'Сбербанк'
        assert len(sber) == 1

    def test_parse_df_malformed_or_blank(self):
        for fixture in (fixtures.meta_malformed__split,
                        fixtures.meta_blank__split):
            fetcher = mock.MagicMock(return_value=fixture)
            meta_file = ExporterMetaFile('https://exampe.com', fetcher)
            with assert_raises(FinamDownloadError):
                meta_file.parse_df()


class TestExporterMeta(object):

    def setup(self):
        with mock.patch('finam.export.ExporterMetaPage'):
            fetcher = mock.MagicMock(return_value=fixtures.meta_valid__split)
            self._meta = ExporterMeta(lazy=False, fetcher=fetcher)

    def test_lookup_by_market(self):
        actual = self._meta.lookup(market=Market.SHARES)
        assert set(actual['market']) == {Market.SHARES}

    def test_lookup_by_markets(self):
        actual = self._meta.lookup(market=[Market.SHARES, Market.BONDS])
        assert set(actual['market']) == {Market.SHARES, Market.BONDS}

    def test_lookup_by_id(self):
        actual = self._meta.lookup(id_=SBER.id)
        assert set(actual.index) == {SBER.id}

    def test_lookup_by_ids(self):
        actual = self._meta.lookup(id_=(SBER.id, MICEX.id))
        assert set(actual.index) == {SBER.id, MICEX.id}

    def test_lookup_by_missing_id(self):
        MISSING_ID = self._meta.meta.index.values.max() + 1
        with assert_raises(FinamObjectNotFoundError):
            self._meta.lookup(id_=MISSING_ID)

    def test_lookup_name_code_by_comparators(self):
        for field in ('name', 'code'):
            field_values = getattr(SBER, field), getattr(MICEX, field)
            field_value = field_values[0]
            for comparator, op in zip((LookupComparator.EQUALS,
                                       LookupComparator.CONTAINS,
                                       LookupComparator.STARTSWITH),
                                      (operator.eq,
                                       operator.contains,
                                       startswith_compat)):

                actual = self._meta.lookup(**{
                    field: field_value, field + '_comparator': comparator
                })
                assert all(op(val, field_value) for val in set(actual[field]))

                actual = self._meta.lookup(**{
                    field: field_values,
                    field + '_comparator': comparator
                })
                for actual_value in set(actual[field]):
                    assert any(op(actual_value, asked_value)
                               for asked_value in field_values)

    def test_lookup_by_market_and_codes(self):
        codes = SBER.code, 'GMKN'
        actual = self._meta.lookup(market=Market.SHARES, code=codes)
        assert len(actual) == len(codes)
        assert set(actual['market']) == {Market.SHARES}


@parameterized([
    (date(2016, 1, 1), date(2020, 1, 30), Timeframe.DAILY,
     ((date(2016, 1, 1), date(2020, 1, 30)),)),
    (date(2016, 1, 1), date(2016, 1, 1), Timeframe.MINUTES1,
     ((date(2016, 1, 1), date(2016, 1, 1)),)),
    (date(2016, 1, 1), date(2016, 1, 2), Timeframe.MINUTES1,
     ((date(2016, 1, 1), date(2016, 1, 2)),)),
    (date(2018, 1, 1), date(2020, 9, 15), Timeframe.MINUTES1,
     ((date(2018, 1, 1), date(2018, 12, 31)),
      (date(2019, 1, 1), date(2019, 12, 31)),
      (date(2020, 1, 1), date(2020, 9, 15)),)),
    (date(2019, 3, 1), date(2020, 3, 1), Timeframe.MINUTES1,
     ((date(2019, 3, 1), date(2020, 2, 28)),
      (date(2020, 2, 29), date(2020, 3, 1)),)),
    (date(2018, 3, 1), date(2019, 3, 1), Timeframe.MINUTES1,
     ((date(2018, 3, 1), date(2019, 2, 28)),
      (date(2019, 3, 1), date(2019, 3, 1)),)),
    (date(2019, 3, 1), date(2020, 2, 29), Timeframe.MINUTES1,
     ((date(2019, 3, 1), date(2020, 2, 28)),
      (date(2020, 2, 29), date(2020, 2, 29)),)),
    (date(2016, 1, 1), date(2016, 1, 1), Timeframe.TICKS,
     ((date(2016, 1, 1), date(2016, 1, 1)),)),
    (date(2020, 2, 29), date(2020, 3, 1), Timeframe.TICKS,
     ((date(2020, 2, 29), date(2020, 2, 29)),
      (date(2020, 3, 1), date(2020, 3, 1)),)),
    (date(2020, 1, 30), date(2020, 2, 1), Timeframe.TICKS,
     ((date(2020, 1, 30), date(2020, 1, 30)),
      (date(2020, 1, 31), date(2020, 1, 31)),
      (date(2020, 2, 1), date(2020, 2, 1)),)),
])
def test_split_interval(start_date, end_date, interval, expected):
    actual = split_interval(start_date, end_date, interval)
    assert expected == actual


def test_split_interval_validation():
    with assert_raises_regexp(ValueError, 'start_date must be'):
        split_interval(date(2020, 1, 1), date(2010, 1, 1), Timeframe.DAILY)
