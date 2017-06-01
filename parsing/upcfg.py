from copy import deepcopy

from nltk.grammar import Nonterminal
from nltk.grammar import induce_pcfg

from parsing.baselines import Flat
from parsing.cky_parser import CKYParser
from parsing.util import lexicalize
from parsing.util import unlexicalize


class UPCFG:
    """Unlexicalized PCFG."""

    def __init__(self, parsed_sents, start='sentence', horzMarkov=None):
        """
        parsed_sents -- list of training trees.
        """
        self.start = start  # Saved as string not as a nonterminal

        productions = []
        for tree in parsed_sents:
            # Copy to avoid modification of the original sentences
            tree = unlexicalize(deepcopy(tree))
            tree.chomsky_normal_form(horzMarkov=horzMarkov)
            tree.collapse_unary(collapsePOS=True)
            productions += tree.productions()

        self.pcfg = induce_pcfg(Nonterminal(start), productions)
        self.parser = CKYParser(self.pcfg)

    def productions(self):
        """Returns the list of UPCFG probabilistic productions.
        """
        return self.pcfg.productions()

    def parse(self, tagged_sent):
        """Parse a tagged sentence.

        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """
        words, tags = zip(*tagged_sent)
        prob, tree = self.parser.parse(tags)
        if tree is None:
            return Flat([], self.start).parse(tagged_sent)

        tree.un_chomsky_normal_form()
        return lexicalize(tree, words)
