from finam.export import Exporter, Market


"""
Simply lists available markets and some samples out of them
"""

SAMPLE_SIZE = 5


def main():
    exporter = Exporter()
    for market in Market:
        print('{0.name:*^25}'.format(market))
        items = exporter.lookup(market=market)
        print('Total items: {}'.format(len(items)))
        print('Sample: {}'.format(', '.join(items['code'][:SAMPLE_SIZE])))


if __name__ == '__main__':
    main()
