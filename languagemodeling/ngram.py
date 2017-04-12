# https://docs.python.org/3/library/collections.html
from collections import defaultdict
from math import log
from random import uniform


class NGram(object):

    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """
        assert n > 0
        self.n = n
        self.counts = counts = defaultdict(int)

        for sent in sents:
            sent = self._add_tags(sent)

            for i in range(len(sent) - n + 1):
                ngram = tuple(sent[i: i + n])
                counts[ngram] += 1
                counts[ngram[:-1]] += 1

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.

        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        n = self.n
        if not prev_tokens:
            prev_tokens = []
        assert len(prev_tokens) == n - 1

        tokens = prev_tokens + [token]
        return float(self.counts[tuple(tokens)]) /\
            self.counts[tuple(prev_tokens)]

    def count(self, tokens):
        """Count for an n-gram or (n-1)-gram.

        tokens -- the n-gram or (n-1)-gram tuple.
        """
        return self.counts[tokens]

    def _add_tags(self, sent):
        """Add (n - 1) opening tags <s> at the beginning of the sentence
        and one closing tag at the end.

        sent -- The sentence.
        """
        return ['<s>'] * (self.n - 1) + sent + ['</s>']

    def sent_prob(self, sent):
        """Probability of a sentence. Warning: subject to underflow problems.

        sent -- the sentence as a list of tokens.
        """
        n = self.n
        probability = 1
        sent = self._add_tags(sent)

        for i in range(n - 1, len(sent)):
            if probability == 0:
                # If the previous token has zero probability, then a call to
                # cond_prob will cause a division by zero, break here to avoid
                # that.
                break
            probability *= self.cond_prob(sent[i], sent[i - n + 1: i])
        return probability

    def sent_log_prob(self, sent):
        """Log-probability of a sentence.

        sent -- the sentence as a list of tokens.
        """
        def log_2(x):
            if x != 0:
                return log(x, 2)
            return float('-inf')

        n = self.n
        probability = 0
        sent = self._add_tags(sent)

        for i in range(n - 1, len(sent)):
            if probability == float('-inf'):
                # If the previous token has -inf probability, then a call to
                # cond_prob will cause a division by zero, break here to avoid
                # that.
                break
            probability += log_2(self.cond_prob(sent[i], sent[i - n + 1: i]))
        return probability


class NGramGenerator:

    def __init__(self, model):
        """
        model -- n-gram model.
        """

    def generate_sent(self):
        """Randomly generate a sentence."""

    def generate_token(self, prev_tokens=None):
        """Randomly generate a token, given prev_tokens.

        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
