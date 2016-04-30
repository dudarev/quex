import string

import snowballstemmer

import config


REMOVE_PUNCTUATION_MAP = dict((ord(char), ord(' ')) for char in string.punctuation)


def stem_and_lower(str_):
    """
    Returns string with unique lowercase words stemmed.
    """
    stemmer = snowballstemmer.stemmer(config.LANGUAGE_FULL)
    str_no_punctuation = str_.translate(REMOVE_PUNCTUATION_MAP)
    str_stemmed = stemmer.stemWords(
        map(
            lambda x: x.lower(),
            set(str_no_punctuation.split())
        )
    )
    return ' '.join(str_stemmed)
