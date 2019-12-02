import re

from wordlist.filters import *

class WordListProcessor:
    """Processes given words and writes them to output controller

    Attributes:
        output_controller (OutputController): output controller for controling
            of output
        charset (str): (default=" _-+=.,;:") set of characters to use when 
            joining sets of words together
        max_combo_length (int): (default=5) max number of words to chain together
            when combining multiple words for a single password
        min_word_length (int): (default=3) minimum length of words to use
        max_word_length (int): (default=15) maximum length of words to use
        smush_words (bool): (default=True) make word chains without connectors
    """

    def __init__(self, output_controller, charset=" _-+=.,;:", max_combo_length=3, min_word_length=3, max_word_length=15, smush_words=True):
        self._output = output_controller
        self._charset = charset
        self._max_combo = max_combo_length
        self._max_word_len = max_word_length
        self._min_word_len = min_word_length
        self._smush_words = smush_words

    def _filter_words(self, word_groups):
        def is_empty(string):
            return str.strip(string) == ""

    def process(self, word_groups):
        """Run the given set of word groups through a set of filters to create
        passwords

        Parameters:
            word_groups (list): list of strings to be turned into passwords
        """

        def is_empty(string):
            return str.strip(string) == ""
            #return string.replace()
        def remove_empty(groups):
            return [ word for word in word_groups if not is_empty(word) ]

        # remove empty words
        word_groups = remove_empty(word_groups)

        filters = [
            FilterNoCaps(),
            FilterNoNumbers(),
            FilterOnlyEnglishLetters(),
            FilterNoSymbols(),
            FilterMakeWordChains()
        ]

        for strain in filters:
            word_groups = strain.filter_words(
                word_groups, 
                charset=self._charset, 
                max_combo=self._max_combo,
                min_length=self._min_word_len,
                max_length=self._max_word_len,
                smush_words=self._smush_words
            )
            word_groups = remove_empty(word_groups)
        
        for word in word_groups:
            self._output.write("{}\n".format(word))
        
