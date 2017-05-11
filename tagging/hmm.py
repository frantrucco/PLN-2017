from collections import defaultdict
from math import log


def log2(x):
    if x == 0:
        return float('-inf')
    return log(x, 2)


class HMM:

    def __init__(self, n, tagset, trans, out):
        """
        n -- n-gram size.
        tagset -- set of tags.
        trans -- transition probabilities dictionary.
        out -- output probabilities dictionary.
        """
        def to_default_dict(d):
            result = defaultdict(lambda: defaultdict(float))
            for k, v in d.items():
                result[k] = defaultdict(float, v)
            return result

        self.n = n
        self.tagset = tagset
        self.out = to_default_dict(out)
        self.trans = to_default_dict(trans)

    def tagset(self):
        """Returns the set of tags.
        """
        return self.tagset

    def trans_prob(self, tag, prev_tags):
        """Probability of a tag.

        tag -- the tag.
        prev_tags -- iterable with the previous n-1 tags
        """
        return self.trans[tuple(prev_tags)][tag]

    def log_trans_prob(self, tag, prev_tags):
        """Log probability of a tag.

        tag -- the tag.
        prev_tags -- iterable with the previous n-1 tags
        """
        return log2(self.trans_prob(tag, prev_tags))

    def out_prob(self, word, tag):
        """Probability of a word given a tag.

        word -- the word.
        tag -- the tag.
        """
        return self.out[tag][word]

    def log_out_prob(self, word, tag):
        """Log probability of a word given a tag.

        word -- the word.
        tag -- the tag.
        """
        return log2(self.out_prob(word, tag))

    def add_opening_and_closing_tags(self, y):
        """Add both opening and closing tags to a list of tags or words

        y -- tagging or sentence.
        """
        return ['<s>'] * (self.n - 1) + y + ['</s>']

    def tag_prob(self, y):
        """Probability of a tagging.
        Warning: subject to underflow problems.

        y -- tagging.
        """
        n = self.n
        y = self.add_opening_and_closing_tags(y)

        prob = 1
        for i in range(n - 1, len(y)):
            tag = y[i]
            prev_tags = y[i - n + 1:i]
            prob *= self.trans_prob(tag, prev_tags)
        return prob

    def prob(self, word, y):
        """
        Joint probability of a sentence and its tagging.
        Warning: subject to underflow problems.

        word -- sentence.
        y -- tagging.
        """
        prob = self.tag_prob(y)
        for word, tag in zip(word, y):
            prob *= self.out_prob(word, tag)
        return prob

    def tag_log_prob(self, y):
        """
        Log-probability of a tagging.

        y -- tagging.
        """
        n = self.n
        y = self.add_opening_and_closing_tags(y)

        prob = 0
        for i in range(n - 1, len(y)):
            tag = y[i]
            prev_tags = y[i - n + 1:i]
            prob += self.log_trans_prob(tag, prev_tags)
        return prob

    def log_prob(self, word, y):
        """
        Joint log-probability of a sentence and its tagging.

        word -- sentence.
        y -- tagging.
        """
        prob = self.tag_log_prob(y)
        for word, tag in zip(word, y):
            prob += self.log_out_prob(word, tag)
        return prob

    def tag(self, sent):
        """Returns the most probable tagging for a sentence.

        sent -- the sentence.
        """
        pass


class ViterbiTagger:

    def __init__(self, hmm):
        """
        hmm -- the HMM.
        """

    def tag(self, sent):
        """Returns the most probable tagging for a sentence.

        sent -- the sentence.
        """
