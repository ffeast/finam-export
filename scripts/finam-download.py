#!/usr/bin/env python
import sys
import time
import os.path
import datetime
import logging
from operator import attrgetter
from functools import partial

import click
from click_datetime import Datetime

from finam import (Exporter,
                   Timeframe,
                   Market,
                   FinamExportError,
                   FinamObjectNotFoundError)
from finam.utils import click_validate_enum


"""
Helper script to download a set of assets
"""

logger = logging.getLogger(__name__)


def _arg_split(ctx, param, value):
    if value is None:
        return value

    try:
        items = value.split(',')
    except ValueError:
        raise click.BadParameter('comma-separated {} is required, got {}'
                                 .format(param, value))
    return items


@click.command()
@click.option('--contracts',
              help='Contracts to lookup',
              required=False,
              callback=_arg_split)
@click.option('--market',
              help='Market to lookup',
              callback=partial(click_validate_enum, Market),
              required=False)
@click.option('--timeframe',
              help='Timeframe to use (DAILY, HOURLY, MINUTES30 etc)',
              default=Timeframe.DAILY.name,
              callback=partial(click_validate_enum, Timeframe),
              required=False)
@click.option('--destdir',
              help='Destination directory name',
              required=True,
              type=click.Path(exists=True, file_okay=False, writable=True,
                              resolve_path=True))
@click.option('--skiperr',
              help='Continue if a download error occurs. False by default',
              required=False,
              default=True,
              type=bool)
@click.option('--lineterm',
              help='Line terminator',
              default='\r\n')
@click.option('--delay',
              help='Seconds to sleep between requests',
              type=click.IntRange(0, 600),
              default=1)
@click.option('--startdate', help='Start date',
              type=Datetime(format='%Y-%m-%d'),
              default='2007-01-01',
              required=False)
@click.option('--enddate', help='End date',
              type=Datetime(format='%Y-%m-%d'),
              default=datetime.date.today().strftime('%Y-%m-%d'),
              required=False)
@click.option('--ext',
              help='Resulting file extension',
              default='csv')
def main(contracts, market, timeframe, destdir, lineterm,
         delay, startdate, enddate, skiperr, ext):
    exporter = Exporter()

    if not any((contracts, market)):
        raise click.BadParameter('Neither contracts nor market is specified')

    market_filter = dict()
    if market:
        market_filter.update(market=Market[market])
        if not contracts:
            contracts = exporter.lookup(**market_filter)['code'].tolist()

    for contract_code in contracts:
        logging.info('Handling {}'.format(contract_code))
        try:
            contracts = exporter.lookup(code=contract_code, **market_filter)
        except FinamObjectNotFoundError:
            logger.error('unknown contract "{}"'.format(contract_code))
            sys.exit(1)
        else:
            contract = contracts.reset_index().iloc[0]

        logger.info(u'Downloading contract {}'.format(contract))
        try:
            data = exporter.download(contract.id,
                                     start_date=startdate,
                                     end_date=enddate,
                                     timeframe=Timeframe[timeframe],
                                     market=Market(contract.market))
        except FinamExportError as e:
            if skiperr:
                logger.error(repr(e))
                continue
            else:
                raise
        destpath = os.path.join(destdir, '{}-{}.{}'
                                .format(contract.code, timeframe, ext))

        data.to_csv(destpath, index=False, line_terminator=lineterm)
        if delay > 0:
            logger.info('Sleeping for {} second(s)'.format(delay))
            time.sleep(delay)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
