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

        features = [tf.word_isdigit,
                    tf.word_istitle,
                    tf.word_isupper,
                    tf.word_lower]

        # Add all features from the previous word
        features += [tf.PrevWord(f) for f in features]

        # Add all possible previous igrams (i in 1,...,n-1)
        # Note that there are at most n-1grams (ngrams would include the
        # current word or would underflow the limits of the sentence)
        features += [tf.NPrevTags(i) for i in range(1, n)]

        # This is way too simple
        vectorizer = ('Vectorizer', Vectorizer(features=features))
        classifier = ('Classifier', LogisticRegression())
        self.pipeline = Pipeline([vectorizer, classifier])

        histories = self.sent_histories(tagged_sents)
        tags = self.sents_tags(tagged_sents)
        self.pipeline.fit(histories, tags)

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