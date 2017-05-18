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

NUMBER_OF_TAGS = 10  # Number of tags that should be printed
NUMBER_OF_WORDS = 5  # Number of words that should be printed
NUMBER_OF_AMBIGUITY_LEVELS = 10  # Number of ambiguity levels (from 0 to L - 1)
ROUNDING_PRECISION = 6  # Number of digits rounded


# Better name than itemgetter(0)
def first(x): return x[0]


# Better name than itemgetter(1)
def second(x): return x[1]


def print_table(table, headers=None):
    tablefmt = 'orgtbl'
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
    word_per_tag = defaultdict(lambda: defaultdict(int))
    tag_per_word = defaultdict(lambda: defaultdict(int))

    for sent in sents:
        for token, tag in sent:
            vocabulary[token] += 1
            tag_vocabulary[tag] += 1
            word_per_tag[tag][token] += 1
            tag_per_word[token][tag] += 1

    number_of_tokens = sum(map(len, sents))

    table = [
        ['Number of Sentences', len(sents)],
        ['Number of tokens', number_of_tokens],
        ['Vocabulary size ', len(vocabulary)],
        ['Tag Vocabulary size', len(tag_vocabulary)],
    ]

    print_table(table, None)

    # Sort tags by frequency
    frequent_tags = sorted(tag_vocabulary.items(), key=second,
                           reverse=True)

    # Choose the most frequent ones
    frequent_tags = frequent_tags[:NUMBER_OF_TAGS]

    table = []
    for tag, freq in frequent_tags:
        # Sort words with the given tag by frequency
        frequent_words = sorted(word_per_tag[tag].items(), key=second,
                                reverse=True)

        # Choose the most frequent ones
        frequent_words = frequent_words[:NUMBER_OF_WORDS]

        # Create a string with the most frequent words for the given tag
        frequent_words = ", ".join(map(first, frequent_words))

        # Calculate the percentage that this tag represents in the total
        # Note that number_of_tags == number_of_tokens
        perc = round(freq / number_of_tokens, ROUNDING_PRECISION)

        # Add this information to the table in order to print it later
        table.append([tag, freq, perc, frequent_words])

    headers = ['Tag', 'Frequency', 'Percentage of total',
               'Most frequent words with the tag']
    print_table(table, headers)

    ambiguity = defaultdict(lambda: list())

    for word, tag_count in tag_per_word.items():
        level = len(tag_count)
        freq = sum(tag_count.values())
        ambiguity[level].append((freq, word))

    table = []
    for level, words in ambiguity.items():
        # Calculate the percentage of words in vocabulary that have level tags
        # Note that we divide by the number of words, not by the number of
        # tokens.
        perc = round(len(words) / len(vocabulary), ROUNDING_PRECISION)

        # Sort the words by decreasing frequency (number of times the word
        # appeared in the text)
        words.sort(reverse=True)

        _, most_frequent_words = list(zip(*words[:NUMBER_OF_WORDS]))
        most_frequent_words = ', '.join(most_frequent_words)
        table.append([level, len(words), perc, most_frequent_words])

    headers = ['Level', 'Frequency', 'Percentage of total',
               'Most frequent words in this level']
    print_table(table, headers)
