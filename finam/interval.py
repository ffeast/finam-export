from datetime import timedelta

from .const import Timeframe


_MAX_DAYS_PER_TIMEFRAME = {
    Timeframe.TICKS: 1,
    Timeframe.MINUTES1: 30 * 5,
    Timeframe.MINUTES5: 30 * 5,
    Timeframe.MINUTES10: 30 * 5,
    Timeframe.MINUTES15: 30 * 5,
    Timeframe.MINUTES30: 30 * 5,
    Timeframe.HOURLY: 30 * 5,
    Timeframe.DAILY: 365 * 5,
    Timeframe.WEEKLY: 365 * 10,
    Timeframe.MONTHLY: 365 * 10,
}


def split_interval(start_date, end_date, timeframe):
    if end_date < start_date:
        raise ValueError('start_date must be >= end_date, but got {} and {}'
                         .format(start_date, end_date))
    delta_days = (end_date - start_date).days + 1
    max_days = _MAX_DAYS_PER_TIMEFRAME[timeframe]
    chunks_count, remainder = divmod(delta_days, max_days)
    if remainder != 0:
        chunks_count += 1
    if chunks_count <= 1:
        return ((start_date, end_date),)
    chunks = []
    offset_start = timedelta(0)
    offset_end = timedelta(max_days)
    for chunk_i in range(chunks_count):
        chunks.append((start_date + offset_start,
                      min(start_date + offset_end - timedelta(1), end_date)))
        offset_start += timedelta(max_days)
        offset_end += timedelta(max_days)
    return tuple(chunks)
