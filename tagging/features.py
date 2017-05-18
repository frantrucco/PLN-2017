from collections import namedtuple

from featureforge.feature import Feature


# sent -- the whole sentence.
# prev_tags -- a tuple with the n previous tags.
# i -- the position to be tagged.
History = namedtuple('History', 'sent prev_tags i')


def word_lower(h):
    """Feature: current lowercased word.

    h -- a history.
    """
    if h.i < 0:
        return 'BOS'
    return h.sent[h.i].lower()


def word_istitle(h):
    """Feature: is current word a title?

    h -- a history.
    """
    if h.i < 0:
        return 'BOS'
    return h.sent[h.i].istitle()


def word_isupper(h):
    """Feature: is current word uppercase?

    h -- a history.
    """
    if h.i < 0:
        return 'BOS'
    return h.sent[h.i].isupper()


def word_isdigit(h):
    """Feature: is current word a digit?

    h -- a history.
    """
    if h.i < 0:
        return 'BOS'
    return h.sent[h.i].isdigit()


def prev_tags(h):
    """Feature: the previous tags of current word

    h -- a history.
    """
    return h.prev_tags


class NPrevTags(Feature):
    def __init__(self, n):
        """Feature: n previous tags tuple.

        n -- number of previous tags to consider.
        """
        assert n > 0
        self.n = n

    def _evaluate(self, h):
        """n previous tags tuple.

        h -- a history.
        """
        return h.prev_tags[-self.n:]  # Given that n > 0 we can use this


class PrevWord(Feature):

    def __init__(self, f):
        """Feature: the feature f applied to the previous word.

        f -- the feature.
        """
        self.f = f

    def _evaluate(self, h):
        """Apply the feature to the previous word in the history.

        h -- the history.
        """
        if h.i < 0:
            return str('BOS')
        history = History(h.sent, h.prev_tags, h.i - 1)
        return str(self.f(history))
