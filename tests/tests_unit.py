# coding: utf-8
import operator
import datetime

import mock
import pandas as pd
from nose.tools import assert_raises

from finam.export import (ExporterMeta,
                          Exporter,
                          Market,
                          Period,
                          LookupComparator,
                          FinamParsingError,
                          FinamTooLongPeriodError,
                          FinamObjectNotFoundError)

from . import fixtures, SBER_ID, MICEX_ID, SBER_CODE, MICEX_CODE


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
        sber = got[(got['code'] == SBER_CODE) & (got['market'] == Market.SHARES)]
        assert sber['name'].values[0] == u'Сбербанк'
        assert len(sber) == 1

    def test_malformed(self):
        self.mock_meta.return_value = fixtures.meta_malformed__split
        with assert_raises(FinamParsingError):
            ExporterMeta(lazy=False)

    def test_malformed_or_blank(self):
        for fixture in (fixtures.meta_malformed__split,
                        fixtures.meta_blank__split):
            self.mock_meta.return_value = fixture
            with assert_raises(FinamParsingError):
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
        got = testee.lookup(id_=SBER_ID)
        assert set(got.index) == {SBER_ID}

        # by ids
        got = testee.lookup(id_=(SBER_ID, MICEX_ID))
        assert set(got.index) == {SBER_ID, MICEX_ID}

        # missing id
        MISSING_ID = testee.meta.index.values.max() + 1
        with assert_raises(FinamObjectNotFoundError):
            testee.lookup(id_=MISSING_ID)

        # for various kinds of code matching
        codes = SBER_CODE, MICEX_CODE
        for comparator, op in zip((LookupComparator.EQUALS,
                                   LookupComparator.CONTAINS,
                                   LookupComparator.STARTSWITH),
                                  (operator.eq,
                                   operator.contains,
                                   unicode.startswith)):

            # single code
            got = testee.lookup(code=SBER_CODE, code_comparator=comparator)
            assert all(op(val, SBER_CODE) for val in set(got['code']))

            # multiple codes
            got = testee.lookup(code=codes)
            assert all(any(op(val, code) for code in codes)
                       for val in set(got['code']))

        # by market and codes
        codes = SBER_CODE, 'GMKN'
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

    def teardown(self):
        super(TestExporter, self).teardown()

    def test_results_except_ticks(self):
        for period in (Period.DAILY, Period.MINUTES30, Period.MONTHLY):
            fixture = 'data_sber_{}'.format(period.name.lower())
            self.mock_exporter.return_value = getattr(fixtures, fixture)
            got = self.exporter.download(SBER_ID, Market.SHARES, period=period)
            assert got.index[1] - got.index[0] > datetime.timedelta(0)
            assert got.columns.equals(pd.Index(['<OPEN>', '<HIGH>', '<LOW>',
                                                '<CLOSE>', '<VOL>']))

    def test_results_ticks(self):
        self.mock_exporter.return_value = fixtures.data_sber_ticks
        got = self.exporter.download(SBER_ID, Market.SHARES,
                                     period=Period.TICKS)
        assert got.index[1] - got.index[0] == datetime.timedelta(0)
        assert got.columns.equals(
            pd.Index(['<TICKER>', '<PER>', '<LAST>', '<VOL>']))

    def test_period_too_long(self):
        self.mock_exporter.return_value = ('some noise\n\n'
                                           + Exporter.ERROR_TOO_MUCH_WANTED
                                           + ' more noise\n').encode('cp1251')
        with assert_raises(FinamTooLongPeriodError):
            self.exporter.download(SBER_ID, Market.SHARES)

    def test_sanity_checks(self):
        self.mock_exporter.return_value = 'some abstract\n\nstring'
        with assert_raises(FinamParsingError):
            self.exporter.download(SBER_ID, Market.SHARES)

    @mock.patch('finam.export.pd.read_csv', return_value=pd.DataFrame())
    def test_remote_calls(self, read_csv_mock):
        # any valid data would do in this mock
        self.mock_exporter.return_value = fixtures.data_sber_daily
        url_pattern = 'http://export.finam.ru/table.csv?sep=3&at=1&e=.csv&d=d&f=table&dtf=1&MSOR=0&tmf=3&mstimever=1&mstime=on&sep2=1&em=3&code=SBER&cn=SBER&df=27&yf=2016&dt=27&datf={datf}&yt=2016&market=1&mf=9&mt=9&p={period}' # noqa
        start_date = datetime.date(2016, 10, 27)
        end_date = datetime.date(2016, 10, 27)
        for period in Period:
            datf = period == period.TICKS and 6 or 5
            expected = url_pattern.format(period=period.value, datf=datf)
            self.exporter.download(SBER_ID, Market.SHARES,
                                   start_date, end_date, period)
            self.mock_exporter.assert_called_once()
            assert expected in self.mock_exporter.call_args[0]
            self.mock_exporter.reset_mock()
