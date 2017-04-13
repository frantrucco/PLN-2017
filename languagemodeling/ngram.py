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

        # Multiply the conditional probabilities of every token given that (n-1)
        # previous tokens occurred
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

    def log_prob(self, sents):
        """Compute the sum of the log probabilities of sents.

        sents -- list of sentences to compute the sum of log probability
        """
        return sum(map(self.sent_prob, sents))

    def cross_entropy(self, sents):
        """ Compute the cross entropy of sents.

        sents -- sentences to compute the cross entropy
        """
        return self.log_prob(sents) / sum(map(len, sents))

    def perplexity(self, sents):
        """Compute the perplexity of sents.

        sents -- sentences to compute the perplexity
        """
        return 2 ** (-self.cross_entropy(sents))


class NGramGenerator:

    def __init__(self, model):
        """
        model -- n-gram model.
        """
        self.n = n = model.n

        self.probs = probs = {}
        """A dictionary that maps from (n-1)gram keys to a dictionary that maps
        from tokens to probabilities. Thus, the probability of the token token
        given that prev_tokens are before token is probs[prev_tokens][token].
        """

        self.sorted_probs = sorted_probs = {}
        """Same as probs but the next tokens probabilities are sorted with the
        following order:
        - First, sort by the probability (descending)
        - Second, sort by lexicographical order the tokens (ascending)
        """

        ngrams = [ngram for ngram in model.counts.keys() if len(ngram) == n]

        for ngram in ngrams:
            probs[ngram[:n - 1]] = {}

        for ngram in ngrams:
            prev_tokens = ngram[:n - 1]
            last_token = ngram[n - 1]
            prob_last_token = model.cond_prob(last_token, list(prev_tokens))
            probs[prev_tokens][last_token] = prob_last_token

        # Sort using the following order:
        # - First, sort by the probability (descending)
        # - Second, sort by lexicographical order the tokens (ascending)
        # Which is equivalent to using a key that swaps tuple elements and
        # makes all probabilities negative and sorting that list of tuples
        # using the following order:
        # - First, sort by the first component (ascending)
        # - Second, sort by the second component (ascending)
        # This is the default ordering for tuples thus we can sort each token
        # using:
        for prev_tokens in probs.keys():
            sorted_probs[prev_tokens] = sorted(probs[prev_tokens].items(),
                                               key=lambda x: (-x[1], x[0]))

    def generate_sent(self):
        """Randomly generate a sentence."""
        n = self.n
        # Add (n-1) opening tags to start the generation
        sentence = ['<s>'] * (n - 1)

        while True:
            # Use the last (n-1) tokens from sentence.
            # If n == 0, take []
            prev_tokens = sentence[-(n-1) or len(sentence):]

            predicted_token = self.generate_token(tuple(prev_tokens))

            # Do not append the closing tag
            if predicted_token == '</s>':
                break
            sentence.append(predicted_token)

        # Delete (n-1) opening tags previously added
        sentence = sentence[n-1:]
        return sentence

    def generate_token(self, prev_tokens=None):
        """Randomly generate a token, given prev_tokens.

        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        choices = self.sorted_probs[prev_tokens]
        r = uniform(0, 1)
        cumulative_probability = 0
        # Sum all probabilities until the cumulative probability is bigger than
        # the random number.
        for choice, probability in choices:
            if cumulative_probability + probability >= r:
                return choice
            cumulative_probability += probability
        assert False, 'This should never be reached'

class AddOneNGram(NGram):

    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """
        NGram.__init__(self, n, sents)
        self.vocabulary = {w for s in sents for w in s}

        self.vocabulary.discard('<s>')
        self.vocabulary.discard('</s>')

    def V(self):
        """
        Size of the vocabulary.
        """
        return len(self.vocabulary) + 1

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.

        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        n = self.n
        V = self.V()

        if not prev_tokens:
            prev_tokens = []

        assert len(prev_tokens) == n - 1

        tokens = tuple(prev_tokens + [token])
        prev_tokens = tuple(prev_tokens)
        return ((self.counts[tokens]) + 1.0) / (self.counts[prev_tokens] + V)
