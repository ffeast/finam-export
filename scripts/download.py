import time
import os.path
import datetime
import logging
from operator import attrgetter
from functools import partial

import click
from click_datetime import Datetime

from finam.export import (Exporter,
                          Timeframe,
                          Market,
                          FinamExportError,
                          FinamObjectNotFoundError)


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


def _validate_enum(enumClass, ctx, param, value):
    if value is not None:
        try:
            enumClass[value]
        except KeyError:
            allowed = map(attrgetter('name'), enumClass)
            raise click.BadParameter('allowed values: {}'
                                     .format(', '.join(allowed)))
    return value


@click.command()
@click.option('--contracts',
              help='Contracts to lookup',
              required=False,
              callback=_arg_split)
@click.option('--market',
              help='Market to lookup',
              callback=partial(_validate_enum, Market),
              required=False)
@click.option('--timeframe',
              help='Timeframe to use (DAILY, HOURLY, MINUTES30 etc)',
              default=Timeframe.DAILY.name,
              callback=partial(_validate_enum, Timeframe),
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
def main(contracts, market, timeframe, destdir, lineterm,
         delay, startdate, enddate, skiperr):
    exporter = Exporter()

    if all((contracts, market)):
        raise click.BadParameter('Either contracts or '
                                 'market must be specified')
    elif not any((contracts, market)):
        raise click.BadParameter('Neither contracts nor market is specified')
    elif market:
        contracts = exporter.lookup(market=Market[market])['code'].tolist()

    for contract_code in contracts:
        logging.info('Handling {}'.format(contract_code))
        try:
            contracts = exporter.lookup(code=contract_code)
        except FinamObjectNotFoundError:
            raise RuntimeError('unknown contract "{}"'.format(contract_code))
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
                logger.error(e.message)
                continue
            else:
                raise
        destpath = os.path.join(destdir, '{}-{}.csv'
                                .format(contract.code, timeframe))
        data.to_csv(destpath, line_terminator=lineterm)
        if delay > 0:
            logger.info('Sleeping for {} second(s)'.format(delay))
            time.sleep(delay)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
