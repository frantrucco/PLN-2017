from collections import defaultdict
from itertools import product
from nltk.tree import Tree


class CKYParser:

    def __init__(self, grammar):
        """
        grammar -- a binarised NLTK PCFG.
        """
        self.grammar = grammar
        self.from_rhs = defaultdict(list)
        for p in grammar.productions():
            lhs, rhs, prob = CKYParser.prod_to_triple(p)
            self.from_rhs[rhs].append((lhs, prob))

    def prod_to_triple(p):
        """Convert the production p to a triple of the form (lhs, rhs, prob)

        Additionally:
            - lhs is converted to a string
            - each element in rhs is converted to a string

        p -- the production rule
        """
        return (str(p.lhs()), tuple(map(str, p.rhs())), p.logprob())

    def binary_rules(self, Bs, Cs):
        """Return a list of 4-tuples of the form (A, B, C, probability of rule)

        Create a list of 4-tuples containing all rules of the from A -> B C
        where B is in Bs and C is in Cs.

        Bs -- list of terminal or nonterminals.
        Cs -- list of terminal or nonterminals.
        """
        from_rhs = self.from_rhs

        binary_rules = []
        for rhs in product(Bs, Cs):
            if rhs in from_rhs and len(rhs) == 2:
                B, C = rhs
                binary_rules += [(A, B, C, prob)
                                 for A, prob in from_rhs[rhs]
                                 if B in Bs and C in Cs]
        return binary_rules

    def parse(self, sent):
        """Parse a sequence of terminals.

        sent -- the sequence of terminals.
        """
        n = len(sent)
        inf = float('inf')
        self._pi = score = {}
        self._bp = back = {}
        for i in range(1, n + 1):
            for j in range(i, n + 1):
                score[(i, j)] = {}
                back[(i, j)] = {}

        from_rhs = self.from_rhs
        for i, word in enumerate(sent):
            for A, prob in from_rhs[(word,)]:
                j = i + 1
                score[(j, j)][A] = prob
                back[(j, j)][A] = Tree(A, [word])

        for span in range(1, n):
            for begin in range(1, n - span + 1):
                end = begin + span
                whole = (begin, end)  # The entire interval
                for split in range(begin, end):
                    left, right = (begin, split), (split + 1, end)

                    # All binary production rules of the form A -> B C where
                    # B is in score[left] and C is in score[right]
                    binary_rules = self.binary_rules(score[left], score[right])

                    for A, B, C, rule_prob in binary_rules:
                        prob = score[left][B]
                        prob += score[right][C]
                        new_prob = prob + rule_prob
                        if A not in score[whole] or score[whole][A] < new_prob:
                            score[whole][A] = new_prob
                            back[whole][A] = Tree(A, [back[left][B],
                                                      back[right][C]])

        start = str(self.grammar.start())
        whole = (1, n)  # The entire sentence
        if whole in score and start in score[whole]:
            return (score[whole][start], back[whole][start])
        return (-inf, None)
