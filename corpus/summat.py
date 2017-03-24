import re
from os import path

from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from nltk.corpus import PlaintextCorpusReader

def _extract_abbrev(regex, text):
    """ Extract abbrevs from text using the given regex.

    All resulting abbrevs will be in lowercase and will not contain a trailing
    period.
    """
    abbrevs = []
    findings = regex.findall(text)
    if (findings):
        for x in findings:
            abbrev = x.split()[0]

            # Remove trailing dot
            abbrev = abbrev[:-1]

            # Abbrev should be in lowercase
            abbrev = abbrev.lower()

            abbrevs.append(abbrev)
    return abbrevs


def _extract_abbrevs(corpus_path):
    """ Extract abbrevs from corpus

    All resulting abbrevs will be in lowercase and will not contain a trailing
    period.
    """
    regexes = {}
    abbrevs = {}

    # Abbrev that are followed by a number
    regexes['Numbers'] = re.compile('[a-zA-Z]+\.\s[1-9]')

    # Abbrev that are followed by a latin number
    regexes['Latin Numbers'] = re.compile('[a-zA-Z]+\.\s[ixv]+')

    # Abbrev that are followed by a parentheses
    regexes['Parentheses'] = re.compile('[a-zA-Z]+\.\)')

    # For every regex there will be a abbrev list: the result of searching the
    # regex expression in the corpus
    for key in regexes.keys():
        abbrevs[key] = []

    with open(corpus_path) as f:
        # Extract all abbrevs from corpus
        for line in f:
            for key in regexes.keys():
                abbrevs[key] += _extract_abbrev(regexes[key], line)

    # Delete all closing parentheses remaining from the regex search
    abbrevs['Parentheses'] = [x[:-1] for x in abbrevs['Parentheses']]

    # All abbrev lists shoud now be sets (to avoid duplicates)
    for key in abbrevs.keys():
        abbrevs[key] = set(abbrevs[key])

    # Create a new abbrev set with the abbrevs from all lists
    abbrevs['All'] = set([j for i in abbrevs.values() for j in i])

    return abbrevs['All']


class SummatCorpusReader(PlaintextCorpusReader):

    def __init__(self, root, fileid):
        """
        Construct a new plaintext corpus reader for a single document
        located at the given root directory.  Example usage:

            >>> root = '../../corpus'
            >>> reader = PlaintextCorpusReader(root, 'summat.txt')

        :param root: The root directory for this corpus.
        :param fileid: A string specifying the filename in this corpus.
        """

        # Extract all the abbreviations from the corpus and add them to the
        # sentence tokenizer
        punkt_param = PunktParameters()
        abbrevs = _extract_abbrevs(path.join(root, fileid))
        punkt_param.abbrev_types = abbrevs
        sent_tokenizer = PunktSentenceTokenizer(punkt_param)

        PlaintextCorpusReader.__init__(self, root, fileid,
                              sent_tokenizer=sent_tokenizer)


summat = SummatCorpusReader('corpus/', 'summat.txt')
