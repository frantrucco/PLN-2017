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
        tagset = hmm.tagset

        self._pi = pi = defaultdict(lambda: defaultdict(tuple))

        opening_tags = ('<s>',) * (n - 1)

        # Initialize table in base cases
        pi[0][opening_tags] = (0.0, [])

        for k, word in enumerate(sent):
            for prev_tags in pi[k]:
                for t in tagset:
                    out = hmm.log_out_prob(word, t)
                    trans = hmm.log_trans_prob(t, prev_tags)

                    # If the probability is 0 it is not necessary to add it to
                    # pi.
                    if out == -inf or trans == -inf:
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
        self.addone = addone

        self.tagset = {tag for sent in tagged_sents for _, tag in sent}
        self.wordset = {word for sent in tagged_sents for word, _ in sent}

        # Generator to save memory
        wordtags = (wt for s in tagged_sents for wt in s)
        self.wordtag_count = defaultdict(float, Counter(wordtags))

        # Create a ngram and (n-1)gram tag counter
        self.tag_gram_count = defaultdict(float)

        for sent in tagged_sents:
            tags = [tag for _, tag in sent]
            tags = self.add_opening_and_closing_tags(tags)

            for i in range(len(sent) + 1):
                ngram = tuple(tags[i: i + n])
                self.tag_gram_count[ngram] += 1.0
                self.tag_gram_count[ngram[:-1]] += 1.0

        self.tagger = ViterbiTagger(self)

    def tcount(self, tokens):
        """Count for an n-gram or (n-1)-gram of tags.

        tokens -- the n-gram or (n-1)-gram tuple of tags.
        """
        # Avoid creating new default values in defaultdict, just return the
        # default value (0.0)
        if tokens in self.tag_gram_count:
            return self.tag_gram_count[tokens]
        return 0.0

    def unknown(self, word):
        """Check if a word is unknown for the model.

        word -- the word.
        """
        return word not in self.wordset

    def trans_prob(self, tag, prev_tags=None):
        """Probability of a tag.

        tag -- the tag.
        prev_tags -- iterable with the previous n-1 tags
        """
        if prev_tags is None:
            prev_tags = tuple()

        tcount = self.tcount
        V = len(self.tagset)

        prev_tags = tuple(prev_tags)
        tags = prev_tags + (tag,)

        if self.addone:
            return (tcount(tags) + 1.0) / (tcount(prev_tags) + V)
        else:
            return tcount(tags) / tcount(prev_tags)

    def out_prob(self, word, tag):
        """Probability of a word given a tag.

        word -- the word.
        tag -- the tag.
        """
        tag_count = self.tcount((tag,))

        if self.unknown(word) or tag_count == 0:
            return 1.0 / len(self.wordset)
        else:
            return self.wordtag_count[(word, tag)] / tag_count

    def tag(self, sent):
        """Returns the most probable tagging for a sentence.

        sent -- the sentence.
        """
        return self.tagger.tag(sent)
