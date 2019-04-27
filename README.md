# finam-export
[![Build Status](https://travis-ci.org/ffeast/finam-export.svg?branch=master)](https://travis-ci.org/ffeast/finam-export)

Python client library to download data from finam.ru

## Capabilities
* Contracts lookup by market categories, id, code, name or their combinations using a rich set of mathching options
* Download data of any timeframe available on finam.ru ranging from ticks to monthly resolution

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
./samples/download.py
*** Current Russian ruble exchange rates ***
... some debugging output omitted ...
            <OPEN>  <HIGH>    <LOW>  <CLOSE>       <VOL>
index
2016-11-07  63.945  64.085  63.6625   63.695  1214085000

[1 rows x 5 columns]
*** Current Brent Oil price ***
INFO:root:Loading data from http://export.finam.ru/table.csv?sep=3&at=1&e=.csv&d=d&f=table&dtf=1&MSOR=0&tmf=3&mstimever=1&mstime=on&sep2=1&em=19473&code=BZ&cn=BZ&df=1&yf=2007&dt=7&datf=5&yt=2016&market=24&mf=0&mt=10&p=8
INFO:root:Decoding response
            <OPEN>  <HIGH>  <LOW>  <CLOSE>  <VOL>
index
2016-11-07   45.95   46.38   45.8    46.01  52605

[1 rows x 5 columns]
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
    logging.basicConfig(level=logging.DEBUG)
    main()
```

# Playing samples
If you have it installed from PyPi just run

```bash
./samples/listing.py
```

If you have cloned it from github:
```bash
pip install -r ./requirements.txt
./samples/listing.py
```

## Technical details
* Targeted to Linux/Mac
* Uses pandas inside, all data returned is pandas DataFrames
* Tested with python2.7 and python3.6+
* Good tests coverage
* Detailed logging of what's going on

## Development
* clone the repo
* `pip install -r ./requirements.txt`
* run tests to ensure all is fine
* `nosetests`
* go ahead and enhance it!
* don't forget to cover your changes with tests
