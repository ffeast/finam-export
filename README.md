# finam-export
[![Build Status](https://travis-ci.org/ffeast/finam-export.svg?branch=master)](https://travis-ci.org/ffeast/finam-export)

Python client library to download data from finam.ru

## Capabilities
* Contracts lookup by market categories, id, code, name or their combinations using a rich set of mathching options
* Downloads data of any timeframe available on finam.ru ranging from ticks to monthly resolution
* Allows to download data for arbitrarily long intervals

## Installation
* `pip install finam-export`

## Samples provided
* `samples/listing.py` - simply lists some contracts from every supported market
* `samples/download.py` - downloads some data and prints it out
* `samples/lookups.py` - shows how you can leverage lookup capabilities

## Utility scripts
* `scripts/finam-download.py` - feature-rich standalone script to download finam's data
* `scripts/finam-lookup.py` - to quickly check what's availble on finam

## Show me something working!
Here's the output
```
*** Current Russian ruble exchange rates ***
INFO:finam.export:Fetching https://www.finam.ru/profile/moex-akcii/gazprom/export/
INFO:finam.export:Fetching https://www.finam.ru/cache/N72Hgd54/icharts/icharts.js
INFO:finam.export:Fetching http://export.finam.ru/table.csv?d=d&f=table&e=.csv&dtf=1&tmf=3&MSOR=0&mstime=on&mstimever=1&sep=3&sep2=1&at=1&p=8&em=182456&market=45&df=1&mf=0&yf=2007&dt=12&mt=8&yt=2020&cn=USD000000TOD&code=USD000000TOD&datf=5
        <DATE>    <TIME>  <OPEN>  <HIGH>  <LOW>  <CLOSE>      <VOL>
2163  20200911  00:00:00   75.19   75.19  74.72    74.95  765709000
*** Current Brent Oil price ***
INFO:finam.export:Fetching http://export.finam.ru/table.csv?d=d&f=table&e=.csv&dtf=1&tmf=3&MSOR=0&mstime=on&mstimever=1&sep=3&sep2=1&at=1&p=8&em=19473&market=24&df=1&mf=0&yf=2007&dt=12&mt=8&yt=2020&cn=BZ&code=BZ&datf=5
        <DATE>    <TIME>  <OPEN>  <HIGH>  <LOW>  <CLOSE>   <VOL>
4206  20200911  00:00:00   39.96   40.34  39.38    39.92  114897
```
and here's the code producing this output:
```
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
    logging.basicConfig(level=logging.INFO)
    main()
```

# Playing samples
If you have cloned it from github:
```bash
pip install -r ./requirements.txt
PYTHONPATH=. ./samples/listing.py
```

## Technical details
* Targeted to Linux/Mac
* Uses pandas inside, all data returned is pandas DataFrames
* Tested with python3.6+
* Good tests coverage
* Detailed logging of what's going on

## Development
* clone the repo
* `pip install -r ./requirements.txt`
* run tests to ensure all is fine
* `nosetests`
* go ahead and enhance it!
* don't forget to cover your changes with tests
