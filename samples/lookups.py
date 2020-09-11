#!/usr/bin/env python
# coding: utf-8
import logging

from finam.export import Exporter, Market, LookupComparator

"""
This sample script shows off lookup capabilities
"""


def main():
    exporter = Exporter()
    print('*** Looking up all RTS futures codes ***')
    res = exporter.lookup(
        market=[Market.FUTURES_ARCHIVE, Market.FUTURES],
        name='RTS-',
        name_comparator=LookupComparator.STARTSWITH)
    print(','.join(res['code']))

    print('*** Looking up Russian Ministry of Finance\'s bonds ***')
    print(exporter.lookup(market=Market.BONDS, name=u'ОФЗ',
                          name_comparator=LookupComparator.STARTSWITH))

    print('*** Looking up Microsoft ***')
    print(exporter.lookup(market=Market.USA, name='Microsoft',
                          name_comparator=LookupComparator.CONTAINS))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
