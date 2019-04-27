# coding: utf-8
import operator
import datetime

import mock
import pandas as pd
from nose.tools import assert_raises

from finam.export import (ExporterMeta,
                          ExporterMetaPage,
                          ExporterMetaFile,
                          Exporter,
                          Market,
                          Timeframe,
                          LookupComparator,
                          FinamDownloadError,
                          FinamParsingError,
                          FinamThrottlingError,
                          FinamTooLongTimeframeError,
                          FinamObjectNotFoundError)
from finam.config import FINAM_CHARSET

from . import fixtures, startswith_compat, urls_equal, SBER, MICEX


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

    @mock.patch('finam.export.ExporterMetaPage')
    def test_lookup(self, _):
        fetcher = mock.MagicMock(return_value=fixtures.meta_valid__split)
        meta = ExporterMeta(lazy=False, fetcher=fetcher)

        # by market
        actual = meta.lookup(market=Market.SHARES)
        assert set(actual['market']) == {Market.SHARES}

        # by markets
        actual = meta.lookup(market=[Market.SHARES, Market.BONDS])
        assert set(actual['market']) == {Market.SHARES, Market.BONDS}

        # by id
        actual = meta.lookup(id_=SBER.id)
        assert set(actual.index) == {SBER.id}

        # by ids
        actual = meta.lookup(id_=(SBER.id, MICEX.id))
        assert set(actual.index) == {SBER.id, MICEX.id}

        # missing id
        MISSING_ID = meta.meta.index.values.max() + 1
        with assert_raises(FinamObjectNotFoundError):
            meta.lookup(id_=MISSING_ID)

        # for various kinds of code and name matching
        for field in ('name', 'code'):
            field_values = getattr(SBER, field), getattr(MICEX, field)
            field_value = field_values[0]
            for comparator, op in zip((LookupComparator.EQUALS,
                                       LookupComparator.CONTAINS,
                                       LookupComparator.STARTSWITH),
                                      (operator.eq,
                                       operator.contains,
                                       startswith_compat)):

                # single value
                actual = meta.lookup(**{
                    field: field_value, field + '_comparator': comparator
                })
                assert all(op(val, field_value) for val in set(actual[field]))

                # multiple values
                actual = meta.lookup(**{
                    field: field_values,
                    field + '_comparator': comparator
                })
                for actual_value in set(actual[field]):
                    # matches any of the queries arguments
                    assert any(op(actual_value, asked_value)
                               for asked_value in field_values)

        # mixed lookup by market and codes
        codes = SBER.code, 'GMKN'
        actual = meta.lookup(market=Market.SHARES, code=codes)
        assert len(actual) == len(codes)
        assert set(actual['market']) == {Market.SHARES}
