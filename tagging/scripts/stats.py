"""Print corpus statistics.

Usage:
  stats.py
  stats.py -h | --help

Options:
  -h --help     this Show screen.
"""
from docopt import docopt

from collections import defaultdict
from corpus.ancora import SimpleAncoraCorpusReader
from tabulate import tabulate

def print_table(table, headers=None):
    tablefmt = 'fancy_grid'
    if headers is None:
        t = tabulate(table, tablefmt=tablefmt)
    else:
        t = tabulate(table, headers, tablefmt=tablefmt)

    print(t)


if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the data
    corpus = SimpleAncoraCorpusReader('ancora/ancora-2.0/')
    sents = list(corpus.tagged_sents())

    vocabulary = defaultdict(int)
    tag_vocabulary = defaultdict(int)

    for sent in sents:
        for token, tag in sent:
            vocabulary[token] += 1
            tag_vocabulary[tag] += 1

    table = [
        ['Number of Sentences', len(sents)],
        ['Number of tokens', sum(map(len, sents))],
        ['Vocabulary size ', len(vocabulary)],
        ['Tag Vocabulary size', len(tag_vocabulary)],
    ]

    print_table(table, None)
