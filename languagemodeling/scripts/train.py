"""Train an n-gram model.

Usage:
  train.py -n <n> [-m <model>] -o <file>
  train.py -h | --help

Options:
  -n <n>        Order of the model.
  -m <model>    Model to use [default: ngram]:
                  ngram: Unsmoothed n-grams.
                  addone: N-grams with add-one smoothing.
  -o <file>     Output model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle

from languagemodeling.ngram import NGram
from languagemodeling.ngram import AddOneNGram

# from corpus.summat import summat as corpus
from corpus.galdos import galdos as corpus


if __name__ == '__main__':
    opts = docopt(__doc__)

    # Load the data
    sents = corpus.sents()

    # Train the model
    n = int(opts['-n'])
    model_type = opts['-m']

    # Choose an ngram or addone
    if model_type in ['ngram', None]:
        model = NGram(n, sents)
    if model_type == 'addone':
        model = AddOneNGram(n, sents)
    else:
        print(__doc__)

    # Save the model
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
