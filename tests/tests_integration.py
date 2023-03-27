import unittest
from datetime import date

from parameterized import parameterized


from finam import Exporter, Market, Timeframe
from fixtures import SBER, SHARES_SESSION_MINUTES


class TestIntegration(unittest.TestCase):

    def setUp(self) -> None:
        self.exporter = Exporter()

    @parameterized.expand([
        (date(2015, 1, 1), date(2016, 1, 1), Timeframe.DAILY),
        (date(2016, 1, 1), date(2018, 1, 1), Timeframe.MINUTES1),
    ])
    def test_basic(self, start_date, end_date, timeframe):
        result = self.exporter.download(SBER.id, Market.SHARES,
                                   start_date=start_date,
                                   end_date=end_date,
                                   timeframe=timeframe)
        count = len(result)
        assert count > 0
        assert result['<DATE>'].min() >= int(start_date.strftime('%Y%m%d'))
        assert result['<DATE>'].max() <= int(end_date.strftime('%Y%m%d'))
        assert result.columns.tolist() == ['<DATE>', '<TIME>',
                                           '<OPEN>', '<HIGH>',
                                           '<LOW>', '<CLOSE>', '<VOL>']

    @parameterized.expand([
        (date(2018, 1, 1), date(2018, 1, 1), Timeframe.DAILY),
    ])
    def test_blank(self, start_date, end_date, timeframe):
        result = self.exporter.download(SBER.id, Market.SHARES,
                                   start_date=start_date,
                                   end_date=end_date,
                                   timeframe=timeframe)
        assert len(result) == 0
        assert result.columns.tolist() == ['<DATE>', '<TIME>',
                                           '<OPEN>', '<HIGH>',
                                           '<LOW>', '<CLOSE>', '<VOL>']

    @parameterized.expand([
        (date(2016, 10, 27), date(2016, 10, 27)),
        (date(2020, 9, 7), date(2020, 9, 9)),
    ])
    def test_ticks(self, start_date, end_date):
        result = self.exporter.download(SBER.id, Market.SHARES,
                                   start_date=start_date,
                                   end_date=end_date,
                                   timeframe=Timeframe.TICKS)
        assert len(result) > SHARES_SESSION_MINUTES * 60
        assert result['<DATE>'].min() >= int(start_date.strftime('%Y%m%d'))
        assert result['<DATE>'].max() <= int(end_date.strftime('%Y%m%d'))
        assert result.columns.tolist() == ['<TICKER>',
                                           '<PER>',
                                           '<DATE>',
                                           '<TIME>',
                                           '<LAST>',
                                           '<VOL>']

    @parameterized.expand([
        (date(2018, 1, 1), date(2018, 1, 1)),
    ])
    def test_ticks_blank(self, start_date, end_date):
        result = self.exporter.download(SBER.id, Market.SHARES,
                                   start_date=start_date,
                                   end_date=end_date,
                                   timeframe=Timeframe.TICKS)
        assert len(result) == 0
        assert result.columns.tolist() == ['<TICKER>',
                                           '<PER>',
                                           '<DATE>',
                                           '<TIME>',
                                           '<LAST>',
                                           '<VOL>']
