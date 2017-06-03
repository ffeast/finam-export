import logging

from finam.export import Exporter, Market, LookupComparator

"""
Full-on example displaying up-to-date values of some important indicators
"""


def main():
    exporter = Exporter()
    print('*** Current Russian ruble exchange rates ***')
    rub = exporter.lookup(name='USDRUB_TOD', market=Market.CURRENCIES)
    assert len(rub) == 1
    data = exporter.download(rub.index[0], market=Market.CURRENCIES)
    print(data.tail(1))

    print('*** Current Brent Oil price ***')
    oil = exporter.lookup(name='Brent', market=Market.COMMODITIES,
                          name_comparator=LookupComparator.EQUALS)
    assert len(oil) == 1
    data = exporter.download(oil.index[0], market=Market.COMMODITIES)
    print(data.tail(1))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
