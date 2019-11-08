import re

__all__ = [
    "FilterNoCaps",
    "FilterNoSymbols",
    "FilterNoNumbers",
    "FilterOnlyEnglishLetters",
    "FilterWordLength",
    "FilterMakeWordChains"
]

class Filter:
    """
    Default filter class, has no filter behavior

    Parameters:
        word_groups (list): list of strings to be filtered
    """
    def filter_words(self, word_groups, **kwargs):
        return word_groups

class FilterNoCaps(Filter):
    """
    Removes capitals from word groups

    Parameters:
        word_groups (list): list of strings to be filtered
    """
    def filter_words(self, word_groups, **kwargs):
        return [ word.lower() for word in word_groups ]

class FilterNoSymbols(Filter):
    """
    Removes characters considered symbols, these are:

    ~`!@#$%^&*()-_=+[{}]\|'";:/?.>,<

    Parameters:
        word_groups (list): list of strings to be filtered
    """
    def filter_words(self, word_groups, **kwargs):
        def strip(word):
            return re.sub(r"([!-/:-@\[-`{-~])", "", word)

        return [ strip(word) for word in word_groups ]

class FilterNoNumbers(Filter):
    """
    Removes numbers from word groups

    Parameters:
        word_groups (list): list of strings to be filtered
    """

    def filter_words(self, word_groups, **kwargs):
        def strip(word):
            return re.sub(r"([\d]+)", "", word)

        return [ strip(word) for word in word_groups ]

class FilterOnlyEnglishLetters(Filter):
    """
    Removes non english letters, effectively anything outside of A-Z,a-z

    Parameters:
        word_groups (list): list of strings to be filtered
    """

    def filter_words(self, word_groups, **kwargs):
        def strip(word):
            return re.sub(r"([^\sA-Za-z]+)", "", word)

        return [ strip(word) for word in word_groups ]

class FilterWordLength(Filter):
    """
    Removes words less than a given length

    Paramters:
        word_groups (list): list of strings to be filtered
        min_length (int): (default=3) minimum length allowed (< removed)
        max_length (int): (default=10) maximum length allowed (> removed)
    """

    def filter_words(self, word_groups, **kwargs):
        min_length = 3
        max_length = 10

        if "min_length" in kwargs:
            min_length = kwargs["min_length"]
        if "max_length" in kwargs:
            max_length = kwargs["max_length"]

        def is_correct_len(word, min_length, max_length):
            word_len = len(word)
            return word_len >= min_length and word_len <= max_length

        return [ word for word in word_groups if is_correct_len(word, min_length, max_length) ]

class FilterMakeWordChains(Filter):
    """
    Create word chains with a given charset up to a max combo length.

    This filter works under the assumption that spaces have not be stripped, as
    space will be used as the delimeter between words.

    Parameters:
        word_groups (list): list of strings to be filtered
        charset (str): (default=" _-+=.,;:")set of characters to bridge words, 
            one character at a time will be used
        max_combo (int): (default=3) max number of words to chain together, note,
            that combo size will increase the number of words exponentially,
            please keep that as a consideration when generating words
        min_length (int): (default=3) min word length to use, otherwise filter
        max_length (int): (default=15) max word length to use, otherwise filter
    """

    def filter_words(self, word_groups, **kwargs):
        self._charset = " _-+=.,;:"
        self._max_combo = 3
        self._min_length = 3
        self._max_length = 15

        if "charset" in kwargs:
            self._charset = kwargs["charset"]
        if "max_combo" in kwargs:
            self._max_combo = kwargs["max_combo"]
        if "min_length" in kwargs:
            self._min_length = kwargs["min_length"]
        if "max_length" in kwargs:
            self._max_length = kwargs["max_length"]

        if self._max_combo <= 0:
            raise Exception("Max combo size must be greater than 0, {} provided".format(self._max_combo))
        if self._min_length <= 0:
            raise Exception("Min word length must be greater than 0, {} provided".format(self._min_length))

        word_chains = []

        # iterate through all words and gather their respective word chains
        for word in word_groups:
            word_chains.extend(
                self._get_chains(
                    word, 
                    self._charset,
                    self._max_combo,
                    self._min_length,
                    self._max_length
                )
            )

        return word_chains

    def _get_chains(self, word, charset, max_combo, min_length, max_length):
        """Get word chains from a set of words, a charset, and a maximum combo size

        Parameters:
            word (str): set of words delimeted by space
            charset (str): charset to join words with
            max_combo (int): maximum combo of words to join together

        Returns:
            list (str): list of word chains

        """

        def is_empty(string):
            return string.strip() == ""
        def is_correct_len(string):
            str_len = len(string)
            return str_len >= min_length and str_len <= max_length

        tokens = word.split(" ")
        # filter empty and word length
        tokens = [ token for token in tokens if not is_empty(token) and is_correct_len(token) ]

        # max combo length of 1 means just return single words
        if max_combo == 1:
            return tokens

        chains = []

        for i in range(1, max_combo):
            chains.extend(
                self._get_lapped_chain(tokens, charset, i)
            )

        return chains

    def _get_lapped_chain(self, tokens, charset, length):
        """Creates a string chains from a set of tokens, a set of joiner characters,
        and a length of chain

        Paramters:
            tokens (list): list of strings to join
            charset (str): charset of glue characters
            length (int): length of chains to gather

        Returns:
            list (str): list of chains
        """

        if length == 1:
            return tokens

        chains = []

        for i in range(0, len(tokens) - length):
            # grab tokens in the current range
            chain = tokens[i:i+length]

            # iterate through the set of characters from the char set 
            for glue in charset:
                chains.append(
                    glue.join(chain)
                )
        
        return chains