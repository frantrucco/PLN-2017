"""
Generate natural language sentences using a language model.
Usage:
  generate.py -i <file> -n <n>
  generate.py -h | --help
Options:
  -i <file>     Language model file.
  -n <n>        Number of sentences to generate.
  -h --help     Show this screen.
"""
from docopt import docopt
from pickle import load

from languagemodeling.ngram import NGramGenerator

if __name__ == '__main__':
    opts = docopt(__doc__)

    languageModelFilename = opts['-i']
    with open(languageModelFilename, 'rb') as f:
        generator = NGramGenerator(load(f))

    opening_symbols = '[(¿¡'
    closing_symbols = '])?!.,;:'

    n = int(opts['-n'])

    for _ in range(n):
        sent = ' '.join(generator.generate_sent())

        # Format sent
        for symbol in opening_symbols:
            sent = sent.replace(symbol + ' ', symbol)

        for symbol in closing_symbols:
            sent = sent.replace(' ' + symbol, symbol)

        print(sent)
