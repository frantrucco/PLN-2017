"""Train a sequence tagger.

Usage:
  train.py [-m <model>] [-n <n>] -o <file>
  train.py -h | --help

Options:
  -m <model>    Model to use [default: base]:
                  base: Baseline
                  mlhmm: Hidden Markov Model
                  memm: MEMM
                  memmlsvc: LinearSVC
                  memmmnb: MultinomialNB
  -n <n>        Order of the model [default: 3]
  -o <file>     Output model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle

from corpus.ancora import SimpleAncoraCorpusReader
from tagging.baseline import BaselineTagger
from tagging.hmm import MLHMM
from tagging.memm import MEMM
from tagging.memm import MEMMMultinomialNaiveBayes
from tagging.memm import MEMMLinearSVC


models = {
    'base': BaselineTagger,
    'mlhmm': MLHMM,
    'memm': MEMM,
    'memmlsvc': MEMMLinearSVC,
    'memmmnb': MEMMMultinomialNaiveBayes
}


if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the data
    files = 'CESS-CAST-(A|AA|P)/.*\.tbf\.xml'
    corpus = SimpleAncoraCorpusReader('ancora/ancora-2.0/', files)
    sents = list(corpus.tagged_sents())

    if opts['-m'] == 'base':
        model_name = opts['-m']
        args = [sents]
    else:
        model_name = opts['-m']
        try:
            n = int(opts['-n'])
        except (TypeError, ValueError) as err:
            print(err)
            print(__doc__)
            exit()

        args = [n, sents]

    # train the model
    model = models[model_name](*args)

    # save it
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
