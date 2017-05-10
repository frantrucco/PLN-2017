from collections import defaultdict


# Better name than itemgetter(0)
def first(x): return x[0]


# Better name than itemgetter(1)
def second(x): return x[1]


class BaselineTagger:

    def __init__(self, tagged_sents):
        """
        tagged_sents -- training sentences, each one being a list of pairs.
        """
        sents = tagged_sents
        tag_per_word = defaultdict(lambda: defaultdict(int))
        word_per_tag = defaultdict(list)

        self.most_frequent_tag = most_frequent_tag = {}

        for sent in sents:
            for token, tag in sent:
                tag_per_word[token][tag] += 1
                word_per_tag[tag].append(token)

        for word, tag_freqs in tag_per_word.items():
            # Sort the tags per word by decreasing frequency
            sorted_tag_freqs = sorted(tag_freqs.items(), key=second,
                                      reverse=True)

            most_frequent_tag[word] = first(sorted_tag_freqs[0])

    def tag(self, sent):
        """Tag a sentence.

        sent -- the sentence.
        """
        return [self.tag_word(word) for word in sent]

    def tag_word(self, word):
        """Tag a word.

        word -- the word.
        """
        if self.unknown(word):
            return 'nc0s000'
        else:
            return self.most_frequent_tag[word]

    def unknown(self, word):
        """Check if a word is unknown for the model.

        word -- the word.
        """
        return word not in self.most_frequent_tag
