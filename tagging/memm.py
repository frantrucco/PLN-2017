from featureforge.vectorizer import Vectorizer
from itertools import chain
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import tagging.features as tf


class MEMM:

    def __init__(self, n, tagged_sents):
        """
        n -- order of the model.
        tagged_sents -- list of sentences, each one being a list of pairs.
        """
        self.n = n
        self._wordset = {w for s in tagged_sents for w, _ in s}

    def sents_histories(self, tagged_sents):
        """
        Iterator over the histories of a corpus.

        tagged_sents -- the corpus (a list of sentences)
        """
        return chain(*(self.sent_histories(s) for s in tagged_sents))

    def sent_histories(self, tagged_sent):
        """
        Iterator over the histories of a tagged sentence.

        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """
        n = self.n
        words, tags = zip(*tagged_sent)
        tags = ('<s>') * (n - 1) + tuple(tags)
        indexes = list(range(len(tagged_sent)))
        prev_tags = [tags[i: i + n - 1] for i in indexes]

        return (tf.History(words, prev_tags[i], i) for i in indexes)

    def sents_tags(self, tagged_sents):
        """
        Iterator over the tags of a corpus.

        tagged_sents -- the corpus (a list of sentences)
        """
        return (t for s in tagged_sents for w, t in s)

    def sent_tags(self, tagged_sent):
        """
        Iterator over the tags of a tagged sentence.

        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """
        return (t for w, t in tagged_sent)

    def tag(self, sent):
        """Tag a sentence.

        sent -- the sentence.
        """

    def tag_history(self, h):
        """Tag a history.

        h -- the history.
        """

    def unknown(self, w):
        """Check if a word is unknown for the model.

        w -- the word.
        """
        return w not in self._wordset
