# https://docs.python.org/3/library/unittest.html
from unittest import TestCase
from math import log2

from nltk.tree import Tree
from nltk.grammar import PCFG

from parsing.cky_parser import CKYParser


class TestCKYParser(TestCase):

    def test_parse(self):
        grammar = PCFG.fromstring(
            """
                S -> NP VP              [1.0]
                NP -> Det Noun          [0.6]
                NP -> Noun Adj          [0.4]
                VP -> Verb NP           [1.0]
                Det -> 'el'             [1.0]
                Noun -> 'gato'          [0.9]
                Noun -> 'pescado'       [0.1]
                Verb -> 'come'          [1.0]
                Adj -> 'crudo'          [1.0]
            """)

        parser = CKYParser(grammar)

        lp, t = parser.parse('el gato come pescado crudo'.split())

        # check chart
        pi = {
            (1, 1): {'Det': log2(1.0)},
            (2, 2): {'Noun': log2(0.9)},
            (3, 3): {'Verb': log2(1.0)},
            (4, 4): {'Noun': log2(0.1)},
            (5, 5): {'Adj': log2(1.0)},

            (1, 2): {'NP': log2(0.6 * 1.0 * 0.9)},
            (2, 3): {},
            (3, 4): {},
            (4, 5): {'NP': log2(0.4 * 0.1 * 1.0)},

            (1, 3): {},
            (2, 4): {},
            (3, 5): {'VP': log2(1.0) + log2(1.0) + log2(0.4 * 0.1 * 1.0)},

            (1, 4): {},
            (2, 5): {},

            (1, 5): {'S':
                     log2(1.0) +
                     log2(0.6 * 1.0 * 0.9) +
                     log2(1.0) + log2(1.0) + log2(0.4 * 0.1 * 1.0)},
        }
        self.assertEqualPi(parser._pi, pi)

        # check partial results
        bp = {
            (1, 1): {'Det': Tree.fromstring("(Det el)")},
            (2, 2): {'Noun': Tree.fromstring("(Noun gato)")},
            (3, 3): {'Verb': Tree.fromstring("(Verb come)")},
            (4, 4): {'Noun': Tree.fromstring("(Noun pescado)")},
            (5, 5): {'Adj': Tree.fromstring("(Adj crudo)")},

            (1, 2): {'NP': Tree.fromstring("(NP (Det el) (Noun gato))")},
            (2, 3): {},
            (3, 4): {},
            (4, 5): {'NP': Tree.fromstring("(NP (Noun pescado) (Adj crudo))")},

            (1, 3): {},
            (2, 4): {},
            (3, 5): {'VP': Tree.fromstring(
                "(VP (Verb come) (NP (Noun pescado) (Adj crudo)))")},

            (1, 4): {},
            (2, 5): {},

            (1, 5): {'S': Tree.fromstring(
                """(S
                    (NP (Det el) (Noun gato))
                    (VP (Verb come) (NP (Noun pescado) (Adj crudo)))
                   )
                """)},
        }
        self.assertEqual(parser._bp, bp)

        # check tree
        t2 = Tree.fromstring(
            """
                (S
                    (NP (Det el) (Noun gato))
                    (VP (Verb come) (NP (Noun pescado) (Adj crudo)))
                )
            """)
        self.assertEqual(t, t2)

        # check log probability
        lp2 = log2(1.0 * 0.6 * 1.0 * 0.9 * 1.0 * 1.0 * 0.4 * 0.1 * 1.0)
        self.assertAlmostEqual(lp, lp2)

    def assertEqualPi(self, pi1, pi2):
        self.assertEqual(set(pi1.keys()), set(pi2.keys()))

        for k in pi1.keys():
            d1, d2 = pi1[k], pi2[k]
            self.assertEqual(d1.keys(), d2.keys(), k)
            for k2 in d1.keys():
                prob1 = d1[k2]
                prob2 = d2[k2]
                self.assertAlmostEqual(prob1, prob2)

    def test_parse_ambiguous(self):
        grammar = PCFG.fromstring(
            """
                S -> NP VP              [0.6]
                S -> NPVP PP            [0.4]

                NP -> Det Noun          [1.0]

                NPVP -> NP VP           [1.0]

                PP -> SPS Noun          [1.0]

                VP -> Verb Noun         [0.5]
                VP -> VerbNoun PP       [0.5]

                VerbNoun -> Verb Noun   [1.0]

                Det -> 'el'             [1.0]
                Noun -> 'gato'          [0.3]
                Verb -> 'come'          [1.0]
                Noun -> 'pescado'       [0.3]
                SPS -> 'con'            [1.0]
                Noun -> 'sal'           [0.4]

            """)

        parser = CKYParser(grammar)

        lp, t = parser.parse('el gato come pescado con sal'.split())

        # check chart
        pi = {
            (1, 1): {'Det': log2(1.0)},
            (2, 2): {'Noun': log2(0.3)},
            (3, 3): {'Verb': log2(1.0)},
            (4, 4): {'Noun': log2(0.3)},
            (5, 5): {'SPS': log2(1.0)},
            (6, 6): {'Noun': log2(0.4)},

            (1, 2): {'NP': log2(1.0 * 0.3 * 1.0)},
            (2, 3): {},
            (3, 4): {'VP': log2(1.0 * 0.3 * 0.5),
                     'VerbNoun': log2(1.0 * 0.3 * 1.0)},
            (4, 5): {},
            (5, 6): {'PP': log2(1.0 * 0.4 * 1.0)},

            (1, 3): {},
            (2, 4): {},
            (3, 5): {},
            (4, 6): {},

            (1, 4): {'NPVP': log2((1.0 * 0.3 * 1.0 * 0.3) *
                                  (1.0 * 0.5) *
                                  1.0),

                     'S': log2((1.0 * 0.3 * 1.0 * 0.3) *
                               (1.0 * 0.5) *
                               0.6)},
            (2, 5): {},
            (3, 6): {'VP': log2((1.0 * 0.3 * 1.0 * 0.4) *
                                (1.0 * 1.0) *
                                0.5)},

            (1, 5): {},
            (2, 6): {},

            (1, 6): {'NPVP': log2((1.0 * 0.3 * 1.0 * 0.3 * 1.0 * 0.4) *
                                  (1.0 * 0.5) *
                                  1.0),
                     'S': log2((1.0 * 0.3 * 1.0 * 0.3 * 1.0 * 0.4) *
                               (1.0 * 0.5) *
                               0.6)},
        }
        self.assertEqualPi(parser._pi, pi)

        # check partial results
        bp = {
            (1, 1): {'Det': Tree.fromstring('(Det el)')},
            (2, 2): {'Noun': Tree.fromstring('(Noun gato)')},
            (3, 3): {'Verb': Tree.fromstring('(Verb come)')},
            (4, 4): {'Noun': Tree.fromstring('(Noun pescado)')},
            (5, 5): {'SPS': Tree.fromstring('(SPS con)')},
            (6, 6): {'Noun': Tree.fromstring('(Noun sal)')},

            (1, 2): {'NP': Tree.fromstring('(NP (Det el) (Noun gato))')},
            (2, 3): {},
            (3, 4): {'VP': Tree.fromstring(
                         '(VP (Verb come) (Noun pescado))'),
                     'VerbNoun': Tree.fromstring(
                         '(VerbNoun (Verb come) (Noun pescado))')},
            (4, 5): {},
            (5, 6): {'PP': Tree.fromstring('(PP (SPS con) (Noun sal))')},

            (1, 3): {},
            (2, 4): {},
            (3, 5): {},
            (4, 6): {},

            (1, 4): {'NPVP': Tree.fromstring(
                     """
                     (NPVP (NP (Det el) (Noun gato))
                           (VP (Verb come) (Noun pescado)))"""),

                     'S': Tree.fromstring(
                     """
                     (S (NP (Det el) (Noun gato))
                        (VP (Verb come) (Noun pescado)))""")},

            (2, 5): {},
            (3, 6): {'VP': Tree.fromstring(
                     """
                    (VP (VerbNoun (Verb come) (Noun pescado))
                        (PP (SPS con) (Noun sal)))""")},

            (1, 5): {},
            (2, 6): {},

            (1, 6): {'NPVP': Tree.fromstring(
                    """
                    (NPVP (NP (Det el) (Noun gato))
                          (VP (VerbNoun (Verb come) (Noun pescado))
                              (PP (SPS con) (Noun sal))))"""),
                     'S': Tree.fromstring(
                    """
                    (S (NP (Det el) (Noun gato))
                       (VP
                           (VerbNoun (Verb come) (Noun pescado))
                           (PP (SPS con) (Noun sal))))""")},
        }
        self.maxDiff = None
        self.assertEqual(parser._bp, bp)
        # check tree
        t2 = Tree.fromstring(
            """
            (S (NP (Det el) (Noun gato))
               (VP
                   (VerbNoun (Verb come) (Noun pescado))
                   (PP (SPS con) (Noun sal))))""")
        self.assertEqual(t, t2)

        # check log probability
        lp2 = log2((1.0 * 0.3 * 1.0 * 0.3 * 1.0 * 0.4) * (1.0 * 0.5) * 0.6)
        self.assertAlmostEqual(lp, lp2)
