# coding: utf-8
import operator
import datetime

import mock
import pandas as pd
from nose.tools import assert_raises

from finam.export import (ExporterMeta,
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


class MockedMetaMixin(object):

    """
    Mixin to have prepared ExporterMeta._fetch mocks for all methods at once
    """

    def setup(self):
        self._patcher_meta = mock.patch('finam.export.ExporterMeta._fetch')
        self.mock_meta = self._patcher_meta.start()

    def teardown(self):
        self._patcher_meta.stop()


class TestExporterMeta(MockedMetaMixin):

    def test_ok(self):
        self.mock_meta.return_value = fixtures.meta_valid__split
        got = ExporterMeta(lazy=False).meta

        # some basic checks
        assert isinstance(got, pd.DataFrame)
        assert got.columns.tolist() == ['name', 'code', 'market']
        assert len(got['market'].unique()) == 32
        assert len(got) > len(got['market'].unique())

        # simple test for a well-known company
        sber = got[(got['code'] == SBER.code)
                   & (got['market'] == Market.SHARES)]
        assert sber['name'].values[0] == u'Сбербанк'
        assert len(sber) == 1

    def test_malformed_or_blank(self):
        for fixture in (fixtures.meta_malformed__split,
                        fixtures.meta_blank__split):
            self.mock_meta.return_value = fixture
            with assert_raises(FinamDownloadError):
                ExporterMeta(lazy=False)

    def test_lookup(self):
        self.mock_meta.return_value = fixtures.meta_valid__split
        testee = ExporterMeta(lazy=False)

        # by market
        got = testee.lookup(market=Market.SHARES)
        assert set(got['market']) == {Market.SHARES}

        # by markets
        got = testee.lookup(market=[Market.SHARES, Market.BONDS])
        assert set(got['market']) == {Market.SHARES, Market.BONDS}

        # by id
        got = testee.lookup(id_=SBER.id)
        assert set(got.index) == {SBER.id}

        # by ids
        got = testee.lookup(id_=(SBER.id, MICEX.id))
        assert set(got.index) == {SBER.id, MICEX.id}

        # missing id
        MISSING_ID = testee.meta.index.values.max() + 1
        with assert_raises(FinamObjectNotFoundError):
            testee.lookup(id_=MISSING_ID)

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
                got = testee.lookup(**{
                    field: field_value, field + '_comparator': comparator
                })
                assert all(op(val, field_value) for val in set(got[field]))

                # multiple values
                got = testee.lookup(**{
                    field: field_values,
                    field + '_comparator': comparator
                })
                for got_value in set(got[field]):
                    # matches any of the queries arguments
                    assert any(op(got_value, asked_value)
                               for asked_value in field_values)

        # mixed lookup by market and codes
        codes = SBER.code, 'GMKN'
        got = testee.lookup(market=Market.SHARES, code=codes)
        assert len(got) == len(codes)
        assert set(got['market']) == {Market.SHARES}


class MockedExporterMixin(object):

    """
    Mixin to have prepared Exporter._fetch mocks for all methods at once
    """

    def setup(self):
        super(MockedExporterMixin, self).setup()
        self._patcher_exporter = mock.patch('finam.export.Exporter._fetch')
        self.mock_exporter = self._patcher_exporter.start()

    def teardown(self):
        super(MockedExporterMixin, self).teardown()
        self._patcher_exporter.stop()


class TestExporter(MockedExporterMixin, MockedMetaMixin):

    def setup(self):
        super(TestExporter, self).setup()
        self.mock_meta.return_value = fixtures.meta_valid__split
        self.exporter = Exporter()

    def test_results_except_ticks(self):
        for timeframe in (Timeframe.DAILY,
                          Timeframe.MINUTES30,
                          Timeframe.MONTHLY):
            fixture = 'data_sber_{}'.format(timeframe.name.lower())
            self.mock_exporter.return_value = getattr(fixtures, fixture)
            got = self.exporter.download(SBER.id, Market.SHARES,
                                         timeframe=timeframe)
            assert got.index[1] - got.index[0] > datetime.timedelta(0)
            assert got.columns.equals(pd.Index(['<OPEN>', '<HIGH>', '<LOW>',
                                                '<CLOSE>', '<VOL>']))
            assert got.sort_index().equals(got)

    def test_results_ticks(self):
        self.mock_exporter.return_value = fixtures.data_sber_ticks
        got = self.exporter.download(SBER.id, Market.SHARES,
                                     timeframe=Timeframe.TICKS)
        assert got.index[1] - got.index[0] == datetime.timedelta(0)
        assert got.columns.equals(
            pd.Index(['<TICKER>', '<PER>', '<LAST>', '<VOL>']))
        # we need a stable sorting algorithm here
        assert got.sort_index(kind='mergesort').equals(got)

    def test_timeframe_too_long(self):
        self.mock_exporter.return_value = ('some noise\n\n'
                                           + Exporter.ERROR_TOO_MUCH_WANTED
                                           + ' noise\n').encode(FINAM_CHARSET)
        with assert_raises(FinamTooLongTimeframeError):
            self.exporter.download(SBER.id, Market.SHARES)

    def test_sanity_checks(self):
        self.mock_exporter.return_value = 'any\nstring'.encode(FINAM_CHARSET)
        with assert_raises(FinamParsingError):
            self.exporter.download(SBER.id, Market.SHARES)

        self.mock_exporter.return_value = (
            '<html><h1>Forbidden: Access is denied</h1></html>')
        with assert_raises(FinamThrottlingError):
            self.exporter.download(SBER.id, Market.SHARES)

    @mock.patch('finam.export.pd.read_csv', return_value=pd.DataFrame())
    def test_remote_calls(self, read_csv_mock):
        # any valid data would do in this mock
        self.mock_exporter.return_value = fixtures.data_sber_daily
        url_pattern = 'http://export.finam.ru/table.csv?sep=3&at=1&e=.csv&d=d&f=table&dtf=1&MSOR=0&tmf=3&mstimever=1&mstime=on&sep2=1&em=3&code=SBER&cn=SBER&df=27&yf=2016&dt=27&datf={datf}&yt=2016&market=1&mf=9&mt=9&p={timeframe}' # noqa
        start_date = datetime.date(2016, 10, 27)
        end_date = datetime.date(2016, 10, 27)
        for timeframe in Timeframe:
            datf = timeframe == Timeframe.TICKS and 6 or 5
            expected = url_pattern.format(timeframe=timeframe.value, datf=datf)
            self.exporter.download(SBER.id, Market.SHARES,
                                   start_date, end_date, timeframe)
            self.mock_exporter.assert_called_once()
            assert urls_equal(expected, self.mock_exporter.call_args[0][0])
            self.mock_exporter.reset_mock()
