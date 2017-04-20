"""
Plot a graph of model.beta.
Usage:
  beta_visualizer.py [-c <corpus>]
  beta_visualizer.py -h | --help
Options:
  -c <corpus>    Corpus to use [default: galdos]:
                  galdos: Galdos
                  summat: Summa Theologica
  -h --help     Show this screen.
"""
from docopt import docopt
import matplotlib.pyplot as plt
import numpy as np

from languagemodeling.ngram import BackOffNGram as BONGram

from corpus.summat import summat
from corpus.galdos import galdos


def plotit(x, y, label=""):
    plt.scatter(np.array(list(x)), np.array(list(y)), label=label,
                alpha=0.5)


if __name__ == '__main__':
    opts = docopt(__doc__)

    corpus_opt = opts['-c'] or 'galdos'

    # Choose an ngram or addone
    if corpus_opt == 'galdos':
        corpus = galdos
    elif corpus_opt == 'summat':
        corpus = summat
    else:
        print(__doc__)
        exit()

    # Load the data
    sents = corpus.sents()

    for order in range(2, 5):
        model = BONGram(order, sents)
        log_probs = model.log_probs
        plotit(log_probs.keys(), log_probs.values(), "N={}".format(order))

    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    plt.title('Log Probabilities of "{}" corpus'.format(corpus_opt))

    plt.xlabel('Beta')
    plt.ylabel('Log Probability')

    plt.show()
