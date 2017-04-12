import re
from os import path

from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize.punkt import PunktParameters
from nltk.corpus import PlaintextCorpusReader


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
        abbrevs = self._extract_abbrevs(path.join(root, fileid))
        punkt_param.abbrev_types = abbrevs
        sent_tokenizer = PunktSentenceTokenizer(punkt_param)

        PlaintextCorpusReader.__init__(self, root, fileid,
                                       sent_tokenizer=sent_tokenizer)

    def _extract_abbrev(self, regex, text):
        """ Extract abbrevs from text using the given regex.

        All resulting abbrevs will be in lowercase and will not contain a
        trailing period.

        :param regex: A regular expresion for finding abbreviations in text

        :param text: The text that contains the abbreviations
        :type text: str

        :return: The abbrevs matched by the regular expresion regex in text.
        :rtype: list(str)
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

    def _extract_abbrevs(self, corpus_path):
        """ Extract abbrevs from the corpus file found in corpus_path

        :param corpus_path: The path to the corpus file
        :type corpus_path: str

        :return: a set of abbreviations
        :rtype: set(str)
        """
        regexes = {}
        abbrevs = {}

        # Abbrev that are followed by a number
        regexes['Numbers'] = re.compile('[a-zA-Z]+\.\s[1-9]')

        # Abbrev that are followed by a latin number
        regexes['Latin Numbers'] = re.compile('[a-zA-Z]+\.\s[ixv]+')

        # Abbrev that are followed by a parentheses
        regexes['Parentheses'] = re.compile('[a-zA-Z]+\.\)')

        # For every regex there will be a abbrev list: the result of searching
        # the regex expression in the corpus
        for key in regexes.keys():
            abbrevs[key] = []

        with open(corpus_path) as f:
            # Extract all abbrevs from corpus
            for line in f:
                for key in regexes.keys():
                    abbrevs[key] += self._extract_abbrev(regexes[key], line)

        # Delete all closing parentheses remaining from the regex search
        abbrevs['Parentheses'] = [x[:-1] for x in abbrevs['Parentheses']]

        # All abbrev lists shoud now be sets (to avoid duplicates)
        for key in abbrevs.keys():
            abbrevs[key] = set(abbrevs[key])

        # Create a new abbrev set with the abbrevs from all lists
        abbrevs['All'] = set([j for i in abbrevs.values() for j in i])

        return abbrevs['All']


summat = SummatCorpusReader('corpus/', 'summat.txt')
""" The Summat Corpus Reader initialized """
