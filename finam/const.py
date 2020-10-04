from enum import IntEnum

__all__ = ['Market',
           'Timeframe',
           ]


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
