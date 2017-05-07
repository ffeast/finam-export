import os.path
import logging

import click

from finam.export import Exporter, Market, FinamObjectNotFoundError


"""
Helper script to download a set of assets
TODO: timeframe support
"""

logger = logging.getLogger(__name__)


def _arg_split(ctx, param, value):
    try:
        items = value.split(',')
    except ValueError:
        raise click.BadParameter('Comma-separated {} is required, got {}'
                                 .format(param, value))

    return items


@click.command()
@click.option('--contracts',
              help='Contracts to lookup',
              required=True,
              callback=_arg_split)
@click.option('--destdir',
              help='Destination directory name',
              required=True,
              type=click.Path(exists=True, file_okay=False, writable=True,
                              resolve_path=True))
def main(contracts, destdir):
    exporter = Exporter()

    for contract_code in contracts:
        logging.info('Handling {}'.format(contract_code))
        try:
            contracts = exporter.lookup(code=contract_code)
        except FinamObjectNotFoundError:
            raise RuntimeError('unknown contract "{}"'.format(contract_code))
        else:
            contract = contracts.reset_index().iloc[0]

        logger.info(u'Downloading contract {}'.format(contract))
        data = exporter.download(contract.id, market=Market(contract.market))
        destpath = os.path.join(destdir, '{}.csv'.format(contract.code))
        data.to_csv(destpath)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
