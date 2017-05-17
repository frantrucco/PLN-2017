"""Evaulate a tagger.

Usage:
  eval.py -i <file> [-o <file>]
  eval.py -h | --help

Options:
  -i <file>     Tagging model file.
  -o <file>     Output image file.
  -h --help     Show this screen.
"""
from docopt import docopt
from sklearn.metrics import confusion_matrix
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np
import pickle
import sys

from corpus.ancora import SimpleAncoraCorpusReader


class ConfusionMatrix(object):
    def __init__(self, y_true, y_pred, labels, normalize):
        self.labels = labels
        self.cm = confusion_matrix(y_true, y_pred, labels)
        if normalize:
            self.cm = np.round(self.cm / np.sum(self.cm), 2)

    def plot(self, title='Confusion matrix', ylabel='True Tag',
             xlabel='Predicted Tag'):
        """
        This function prints and plots the confusion matrix.
        Normalization can be applied by setting `normalize=True`.
        """
        labels = self.labels
        cm = self.cm
        np.set_printoptions(precision=2)

        plt.figure(figsize=(10, 10), dpi=110)
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Greens)
        plt.title(title)
        plt.colorbar()

        tick_marks = np.arange(len(labels))
        plt.xticks(tick_marks, labels, rotation=90, fontsize=9)
        plt.yticks(tick_marks, labels, fontsize=9)

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    def show(self):
        plt.show()

    def savefig(self, output_filename):
        plt.savefig(output_filename)

    def __str__(self, tablefmt='fancy_grid'):
        table = self.cm * 100
        table = [list(map(str, list(row))) for row in table]
        table = [[self.labels[i]] + row for i, row in enumerate(table)]
        t = tabulate(table, self.labels, tablefmt=tablefmt)
        return str(t)


class Score(object):
    def __init__(self):
        self._hits = 0
        self._total = 0
        self._acc = 0.0

    def update(self, new_hits, added):
        self._hits += new_hits
        self._total += added
        self._acc = float(self._hits) / self._total

    def acc(self):
        return self._acc * 100

    def acc_str(self):
        return '{:2.2f}%'.format(self.acc())


class Progress(object):
    def __init__(self, n, spaces=8):
        template = ['Progress: {:3.1f}%',
                    'Global accuracy: {:2.2f}%,',
                    'Known accuracy: {:2.2f}%,',
                    'Unknown accuracy: {:2.2f}%']
        self.template = (' ' * spaces).join(template)

        self.headers = ['Global accuracy',
                        'Known words accuracy',
                        'Unknown words accuracy']
        self.n = n
        self.i = 0
        self.global_score = Score()
        self.known_score = Score()
        self.unknown_score = Score()

    def update_scores(self, hits_sent, hits_known):
        sum_hits_sent = sum(hits_sent)
        sum_hits_known = sum(hits_known)

        self.global_score.update(sum_hits_sent, len(sent))
        self.known_score.update(sum_hits_known, len(hits_known))
        self.unknown_score.update(sum_hits_sent - sum_hits_known,
                                  len(hits_sent) - len(hits_known))

    def show(self):
        msg = (self.template.format(float(self.i) * 100 / self.n,
                                    self.global_score.acc(),
                                    self.known_score.acc(),
                                    self.unknown_score.acc()))
        print(msg, end='\r')
        sys.stdout.flush()
        self.i += 1
        if self.i == self.n:
            print()  # Avoid next print to be on the same line

    def print_scores(self, tablefmt='fancy_grid'):
        scores = (self.global_score, self.known_score, self.unknown_score)
        table = [[s.acc_str() for s in scores]]
        t = tabulate(table, self.headers, tablefmt=tablefmt)
        print(t)


if __name__ == '__main__':
    opts = docopt(__doc__)

    # Load the model
    filename = opts['-i']
    f = open(filename, 'rb')
    model = pickle.load(f)
    f.close()

    # Get the output filename, if any
    output_filename = opts['-o']
    should_show_cm = output_filename is None or '.png' not in output_filename
    should_savefig = not should_show_cm

    # Load the data
    files = '3LB-CAST/.*\.tbf\.xml'
    corpus = SimpleAncoraCorpusReader('ancora/ancora-2.0/', files)
    sents = list(corpus.tagged_sents())

    # Initialize scores
    progress = Progress(len(sents))

    y_true = []
    y_pred = []
    for i, sent in enumerate(sents):
        word_sent, true_tags = zip(*sent)
        pred_tags = model.tag(word_sent)
        assert len(pred_tags) == len(true_tags), i

        hits_sent = [m == g for m, g in zip(pred_tags, true_tags)]
        hits_known = [hits_sent[j] for j, word in enumerate(word_sent) if
                      not model.unknown(word)]

        progress.update_scores(hits_sent, hits_known)

        y_true += [t for p, t in zip(pred_tags, true_tags) if p != t]
        y_pred += [p for p, t in zip(pred_tags, true_tags) if p != t]

        progress.show()

    progress.print_scores()

    labels = set(y_true).union(set(y_pred))
    labels = sorted(labels)

    cm = ConfusionMatrix(y_true, y_pred, labels, True)
    cm.plot()

    if should_show_cm:
        cm.show()
    if should_savefig:
        cm.savefig(output_filename)
