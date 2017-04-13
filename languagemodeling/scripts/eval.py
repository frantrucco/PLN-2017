"""Evaluate a language model using the test set.

Usage:
  eval.py -i <file>
  eval.py -h | --help

Options:
  -i <file>     Language model file.
  -h --help     Show this screen.
"""
from docopt import docopt
from pickle import load

# from corpus.summat import summat as corpus
from corpus.galdos import galdos_test as corpus

if __name__ == '__main__':
    opts = docopt(__doc__)

    model_filename = opts['-i']

    with open(model_filename, 'rb') as f:
        model = load(f)

    validation_sents = corpus.sents()

    print("Cross Entropy: ",   (model.cross_entropy(validation_sents)))
    print("Perplexity: ",      (model.perplexity(validation_sents)))
