"""Evaulate a parser.

Usage:
  eval.py -i <file> [-m <m>] [-n <n>]
  eval.py -h | --help

Options:
  -i <file>     Parsing model file.
  -m <m>        Parse only sentences of length <= <m>.
  -n <n>        Parse only <n> sentences (useful for profiling).
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle
import sys

from corpus.ancora import SimpleAncoraCorpusReader

from parsing.util import spans


class Progress():
    def __init__(self, labeled, unlabeled, n):
        self.fmt = '{:3.1f}% ({}/{})' + \
            ' L: (P={:2.2f}%, R={:2.2f}%, F1={:2.2f}%)' + \
            ' U: (P={:2.2f}%, R={:2.2f}%, F1={:2.2f}%)'
        self.labeled = labeled
        self.unlabeled = unlabeled
        self.n = n

    def progress(msg, width=None):
        """Ouput the progress of something on the same line."""
        if not width:
            width = len(msg)
        print('\b' * width + msg, end='')
        sys.stdout.flush()

    def print_progress(self, i):
        l = self.labeled
        u = self.unlabeled
        n = self.n
        Progress.progress(self.fmt.format(float(i+1) * 100 / n, i+1, n,
                                          l.prec, l.rec, l.f1,
                                          u.prec, u.rec, u.f1))

    def print_stats(score):
        print('  Precision: {:2.2f}% '.format(score.prec))
        print('  Recall: {:2.2f}% '.format(score.rec))
        print('  F1: {:2.2f}% '.format(score.f1))

    def print_final_scores(self):
        print()
        print()
        print('Parsed {} sentences'.format(n))
        print('Labeled')
        Progress.print_stats(self.labeled)
        print('Unlabeled')
        Progress.print_stats(self.unlabeled)


class Score():
    def __init__(self):
        self.hits = 0
        self.total_gold = 0
        self.total_model = 0
        self.prec = 0
        self.rec = 0
        self.f1 = 0

    def update(self, gold_spans, model_spans):
        self.hits += len(gold_spans & model_spans)
        self.total_gold += len(gold_spans)
        self.total_model += len(model_spans)
        self.prec = float(self.hits) / self.total_model * 100
        self.rec = float(self.hits) / self.total_gold * 100
        self.f1 = 2 * self.prec * self.rec / (self.prec + self.rec)


if __name__ == '__main__':
    opts = docopt(__doc__)

    print('Loading model...')
    filename = opts['-i']
    f = open(filename, 'rb')
    model = pickle.load(f)
    f.close()

    print('Loading corpus...')
    files = '3LB-CAST/.*\.tbf\.xml'
    corpus = SimpleAncoraCorpusReader('ancora/ancora-2.0/', files)
    parsed_sents = list(corpus.parsed_sents())

    if opts['-m'] is not None:
        # Parse only sentences of length <= <m>.
        m = int(opts['-m'])
        parsed_sents = filter(lambda sent: len(sent) <= m, parsed_sents)

    if opts['-n'] is not None:
        # Parse only <n> sentences
        n = int(opts['-n'])
        parsed_sents = parsed_sents[:n]

    print('Parsing...')

    labeled = Score()
    unlabeled = Score()
    n = len(parsed_sents)

    p = Progress(labeled, unlabeled, n)
    p.print_progress(n)
    for i, gold_parsed_sent in enumerate(parsed_sents):
        tagged_sent = gold_parsed_sent.pos()

        # Parse
        model_parsed_sent = model.parse(tagged_sent)

        # Compute labeled scores
        gold_spans = spans(gold_parsed_sent, unary=False)
        model_spans = spans(model_parsed_sent, unary=False)
        labeled.update(gold_spans, model_spans)

        # Ignore label just take in account the interval
        gold_spans = set(map(lambda x: x[1:], gold_spans))
        model_spans = set(map(lambda x: x[1:], model_spans))
        unlabeled.update(gold_spans, model_spans)

        p.print_progress(i)

    p.print_final_scores()
