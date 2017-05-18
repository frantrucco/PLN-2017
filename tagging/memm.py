from featureforge.vectorizer import Vectorizer
from itertools import chain
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
import tagging.features as tf


class MEMM:

    def __init__(self, n, tagged_sents, features=None, classifier=None):
        """
        n -- order of the model.
        tagged_sents -- list of sentences, each one being a list of pairs.
        """
        self.n = n
        self._wordset = {w for s in tagged_sents for w, _ in s}
        self.histories = list(self.sents_histories(tagged_sents))
        self.tags = list(self.sents_tags(tagged_sents))
        if features is None:
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

        if classifier is None:
            classifier = ('Classifier', LogisticRegression())
        else:
            classifier = ('Classifier', classifier)

        vectorizer = ('Vectorizer', Vectorizer(features=features))
        self.pipeline = Pipeline([vectorizer, classifier])

        self.pipeline.fit(self.histories, self.tags)

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
        if tagged_sent == []:
            return iter([])
        n = self.n
        words, tags = zip(*tagged_sent)
        words = list(words)
        tags = ('<s>',) * (n - 1) + tuple(tags)
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
        tags = [None] * len(sent)
        prev_tags = ('<s>',) * (self.n - 1)

        for i in range(len(sent)):
            h = tf.History(sent, prev_tags, i)
            tags[i] = self.tag_history(h)
            prev_tags = prev_tags[1:] + (tags[i],)

        return tags

    def tag_history(self, h):
        """Tag a history.

        h -- the history.
        """
        # Predict returns a list with a single element
        return self.pipeline.predict([h])[0]

    def unknown(self, w):
        """Check if a word is unknown for the model.

        w -- the word.
        """
        return w not in self._wordset


class MEMMMultinomialNaiveBayes(MEMM):
    def __init__(self, n, tagged_sents, features=None):
        classifier = MultinomialNB()
        super().__init__(n, tagged_sents, features, classifier)


class MEMMLinearSVC(MEMM):
    def __init__(self, n, tagged_sents, features=None):
        classifier = LinearSVC()
        super().__init__(n, tagged_sents, features, classifier)
