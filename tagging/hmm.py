from collections import defaultdict
from collections import Counter
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
        self._tagset = tagset
        self._out = out
        self._trans = trans

    def tagset(self):
        """Returns the set of tags.
        """
        return self._tagset

    def trans_prob(self, tag, prev_tags):
        """Probability of a tag.

        tag -- the tag.
        prev_tags -- iterable with the previous n-1 tags
        """
        prev_tags = tuple(prev_tags)
        if prev_tags in self._trans and tag in self._trans[prev_tags]:
            return self._trans[prev_tags][tag]
        return 0.0

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
        if tag in self._out and word in self._out[tag]:
            return self._out[tag][word]
        return 0.0

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
            prev_tags = tuple(y[i - n + 1:i])
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
            prev_tags = tuple(y[i - n + 1:i])
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
        return ViterbiTagger(self).tag(sent)


class ViterbiTagger:

    def __init__(self, hmm):
        """
        hmm -- the HMM.
        """
        self.hmm = hmm

    def tag(self, sent):
        """Returns the most probable tagging for a sentence.

        sent -- the sentence.
        """
        hmm = self.hmm
        n = hmm.n
        inf = float('inf')
        tagset = hmm.tagset()

        self._pi = pi = defaultdict(lambda: defaultdict(tuple))

        opening_tags = ('<s>',) * (n - 1)

        # Initialize table in base cases
        pi[0][opening_tags] = (0.0, [])

        for k, word in enumerate(sent):
            for t in tagset:
                out = hmm.log_out_prob(word, t)

                # If the probability is 0 it is not necessary to add it to
                # pi.
                if out == -inf:
                    continue

                for prev_tags in pi[k]:
                    trans = hmm.log_trans_prob(t, prev_tags)

                    # If the probability is 0 it is not necessary to add it to
                    # pi.
                    if trans == -inf:
                        continue

                    # The probability it is not 0

                    # The maximum probability of a tag sequence ending in tags
                    # prev_tags at position k and the path (sequence of tags)
                    # that results in that maximum probability.
                    max_prob_k, max_path_k = pi[k][prev_tags]

                    prob = out + trans + max_prob_k

                    tags = (prev_tags + (t,))[1:]  # t_{n - 1} ... t_2 t

                    # The recursive formula is:
                    # maximum value for every possible t in tagset of:
                    # out(word, t) + trans(t, prev_tags) + max_prob_k
                    # To obtain this we use pi[k+1][tags] as a placeholder for
                    # the maximum value, i.e., the value of pi[k+1][tags] will
                    # always contain the maximum known probability and path.
                    # When a higher value is obtained by using a different tag,
                    # the value of pi[k+1][tags] will be changed accordingly.

                    if tags in pi[k + 1]:
                        # There is a previous max probability in pi[k+1][tags]
                        current_max_prob, _ = pi[k + 1][tags]
                    else:
                        # This is the first time we set pi[k+1][tags]
                        current_max_prob = -inf

                    if prob > current_max_prob:
                        # Change the value of the probability saved in
                        # pi[k+1][tags] given that we have found a path with a
                        # higher probability.
                        pi[k + 1][tags] = (prob, max_path_k + [t])

        # Return the path with highest probability from the start of the sent
        # to the end of it.
        k = len(sent)
        prob, path = max(pi[k].values())

        # If we wanted to return the probability of the tagging sentence we
        # would need to multiply prob by log_trans_prob('</s>', path[-n:])
        return path


class MLHMM(HMM):
    def __init__(self, n, tagged_sents, addone=True):
        """
        n -- order of the model.
        tagged_sents -- training sentences, each one being a list of pairs.
        addone -- whether to use addone smoothing (default: True).
        """
        # tagset -- set of tags.
        # trans -- transition probabilities dictionary.
        # out -- output probabilities dictionary.
        self.n = n
        self._addone = addone

        self._tagset = {tag for sent in tagged_sents for _, tag in sent}
        self._wordset = {word for sent in tagged_sents for word, _ in sent}

        wordtags = [wt for s in tagged_sents for wt in s]
        self._wordtag_count = dict(Counter(wordtags))

        # Create a ngram (n-1)gram and 1gram tag counter
        # 1gram counts are required in out_prob
        if n > 2:
            # Only count 1grams if they will not be counted (n > 2)
            tags = [(t,) for s in tagged_sents for _, t in s]
            self._tag_gram_count = defaultdict(float, Counter(tags))
        else:
            self._tag_gram_count = defaultdict(float)

        # Count ngram, n-1gram
        for sent in tagged_sents:
            tags = [tag for _, tag in sent]
            tags = self.add_opening_and_closing_tags(tags)
            for i in range(len(sent) + 1):
                ngram = tuple(tags[i: i + n])
                self._tag_gram_count[ngram] += 1.0
                self._tag_gram_count[ngram[:-1]] += 1.0

        self._tag_gram_count = dict(self._tag_gram_count)
        self.tagger = ViterbiTagger(self)

    def tcount(self, tokens):
        """Count for an n-gram or (n-1)-gram of tags.

        tokens -- the n-gram or (n-1)-gram tuple of tags.
        """
        if tokens in self._tag_gram_count:
            return self._tag_gram_count[tokens]
        return 0.0

    def unknown(self, word):
        """Check if a word is unknown for the model.

        word -- the word.
        """
        return word not in self._wordset

    def trans_prob(self, tag, prev_tags=None):
        """Probability of a tag.

        tag -- the tag.
        prev_tags -- iterable with the previous n-1 tags
        """
        if prev_tags is None:
            prev_tags = tuple()

        tcount = self.tcount
        V = len(self._tagset)

        prev_tags = tuple(prev_tags)
        tags = prev_tags + (tag,)

        if self._addone:
            return (tcount(tags) + 1.0) / (tcount(prev_tags) + V)
        return tcount(tags) / tcount(prev_tags)

    def out_prob(self, word, tag):
        """Probability of a word given a tag.

        word -- the word.
        tag -- the tag.
        """
        tag_count = self.tcount((tag,))

        if self.unknown(word) or tag_count == 0:
            return 1.0 / len(self._wordset)
        elif (word, tag) in self._wordtag_count:
            return self._wordtag_count[(word, tag)] / tag_count
        else:
            return 0.0

    def tag(self, sent):
        """Returns the most probable tagging for a sentence.

        sent -- the sentence.
        """
        return self.tagger.tag(sent)
