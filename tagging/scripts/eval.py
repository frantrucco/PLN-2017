"""Evaulate a tagger.

Usage:
  eval.py -i <file> [-o <file>]
  eval.py -h | --help

Options:
  -i <file>     Tagging model file.
  -o <file>     Output image file.
  -h --help     Show this screen.
"""
from collections import defaultdict
from docopt import docopt
from sklearn.metrics import confusion_matrix
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np
import pickle
import sys

from corpus.ancora import SimpleAncoraCorpusReader

TAB_SPACES = 8  # Output formatting


def plot_confusion_matrix(cm, labels, title='Confusion matrix',
                          cmap=plt.cm.Greens):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(labels))
    plt.xticks(tick_marks, labels, rotation=90, fontsize=5)
    plt.yticks(tick_marks, labels, fontsize=5)

    plt.tight_layout()
    plt.ylabel('True tag')
    plt.xlabel('Predicted tag')


def print_table(table, headers=None, row_headers=None):
    tablefmt = 'fancy_grid'
    if row_headers is not None:
        table = [list(map(str, list(row))) for row in table]
        table = [[row_headers[i]] + row for i, row in enumerate(table)]

    if headers is None:
        t = tabulate(table, tablefmt=tablefmt)
    else:
        t = tabulate(table, headers, tablefmt=tablefmt)

    print(t)


def progress(msg, width=None):
    """Ouput the progress of something on the same line."""
    if not width:
        width = len(msg)
    print('\b' * width + msg, end='')
    sys.stdout.flush()


if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the model
    filename = opts['-i']
    f = open(filename, 'rb')
    model = pickle.load(f)
    f.close()

    # load the data
    files = '3LB-CAST/.*\.tbf\.xml'
    corpus = SimpleAncoraCorpusReader('ancora/ancora-2.0/', files)
    sents = list(corpus.tagged_sents())

    # tag
    total = defaultdict(int)
    hits = defaultdict(int)
    acc = defaultdict(int)
    n = len(sents)

    y_true = []
    y_pred = []
    for i, sent in enumerate(sents):
        word_sent, gold_tag_sent = zip(*sent)

        model_tag_sent = model.tag(word_sent)
        assert len(model_tag_sent) == len(gold_tag_sent), i

        # Global score
        hits_sent = [m == g for m, g in zip(model_tag_sent, gold_tag_sent)]
        hits['global'] += sum(hits_sent)
        total['global'] += len(sent)
        acc['global'] = float(hits['global']) / total['global']

        # Known and unknown words score
        hits_known = [hits_sent[j] for j, word in enumerate(word_sent) if
                      not model.unknown(word)]

        hits['known'] += sum(hits_known)
        total['known'] += len(hits_known)
        acc['known'] = hits['known'] / total['known']

        hits['unknown'] += sum(hits_sent) - sum(hits_known)
        total['unknown'] += len(hits_sent) - len(hits_known)
        acc['unknown'] = hits['unknown'] / total['unknown']

        template = ['Progress: {:3.1f}%',
                    'Global accuracy: {:2.2f}%,',
                    'Known accuracy: {:2.2f}%,',
                    'Unknown accuracy: {:2.2f}%']

        template = (' ' * TAB_SPACES).join(template)

        progress(template.format(float(i) * 100 / n,
                                 acc['global'] * 100,
                                 acc['known'] * 100,
                                 acc['unknown'] * 100))

        for j, is_hit in enumerate(hits_sent):
            # If is an error add it to the list
            if not is_hit:
                y_true.append(gold_tag_sent[j])
                y_pred.append(model_tag_sent[j])

    print('')
    headers = ['Global accuracy',
               'Known words accuracy',
               'Unknown words accuracy']

    table = [['{:2.2f}%'.format(a * 100) for a in acc.values()]]

    print_table(table, headers)

    # The labels is the set of all labels, but they must be sorted
    # to avoid non-deterministic behavior
    labels = set(y_true).union(set(y_pred))
    labels = sorted(labels)
    labels = list(labels)

    cm = confusion_matrix(y_true, y_pred, labels)
    # Normalize by the total amount of errors
    cm = np.round(cm / np.sum(cm), 2)

    print_table(cm * 100, labels, labels)

    np.set_printoptions(precision=2)
    plt.figure()
    plot_confusion_matrix(cm, labels)

    output_filename = opts['-o']
    if output_filename is not None and '.png' in output_filename:
        plt.savefig(output_filename)
    else:
        plt.show()
