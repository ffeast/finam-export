from datetime import timedelta, datetime

from finam.export import Exporter, Market, Period

from . import SBER, SHARES_SESSION_MINUTES


class TestIntegration(object):

    def test_basic_but_ticks(self):
        exporter = Exporter()
        start_date = datetime(2015, 1, 1)
        end_date = datetime(2016, 1, 1)

        got_daily = exporter.download(SBER.id, Market.SHARES,
                                      start_date=start_date,
                                      end_date=end_date,
                                      period=Period.DAILY)
        daily_count = len(got_daily)
        assert daily_count > 0

        got_minutes = exporter.download(SBER.id, Market.SHARES,
                                        start_date=start_date,
                                        end_date=end_date,
                                        period=Period.MINUTES30)
        minutes30_count = len(got_minutes)
        assert minutes30_count > daily_count * SHARES_SESSION_MINUTES / 30

        for got in (got_daily, got_minutes):
            assert got.index.min().to_datetime() >= start_date
            assert got.index.max().to_datetime() <= end_date
            assert '<LAST>' not in got.columns
            assert '<CLOSE>' in got.columns

    def test_ticks(self):
        exporter = Exporter()
        ticks_date = datetime(2016, 10, 27)
        got = exporter.download(SBER.id, Market.SHARES,
                                start_date=ticks_date,
                                end_date=ticks_date,
                                period=Period.TICKS)
        assert len(got) > SHARES_SESSION_MINUTES * 60
        assert got.index.min().to_datetime() >= ticks_date
        assert got.index.min().to_datetime() < ticks_date + timedelta(days=1)
        assert '<LAST>' in got.columns
        assert '<CLOSE>' not in got.columns
