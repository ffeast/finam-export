#!/usr/bin/env python
import logging
from functools import partial

import click
import pandas as pd

from finam import Exporter, Market, FinamObjectNotFoundError
from finam.utils import click_validate_enum


"""
Helper script to quickly lookup available contracts
"""

logger = logging.getLogger(__name__)


@click.command()
@click.option('--contract', help='Contract to lookup', required=False)
@click.option('--market',
              help='Market to lookup',
              callback=partial(click_validate_enum, Market),
              required=False)
def main(contract, market):
    exporter = Exporter()

    if all((contract, market)):
        raise click.BadParameter('Either contract or market must be specified')
    elif not any((contract, market)):
        raise click.BadParameter('Neither contract nor market is specified')

    pd.options.display.max_rows = 1000

    if contract:
        try:
            meta = exporter.lookup(code=contract)
        except FinamObjectNotFoundError:
            logger.info('No such contract')
        else:
            print(meta)
    else:
        contracts = exporter.lookup(market=Market[market])
        print(contracts)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
