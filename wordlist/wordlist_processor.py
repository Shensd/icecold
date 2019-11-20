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
    """

    def __init__(self, output_controller, charset=" _-+=.,;:", max_combo_length=5):
        self._output = output_controller
        self._charset = charset
        self._max_combo = max_combo_length

    def _filter_words(self, word_groups):
        def is_empty(string):
            return string.strip() == ""
        

    def process(self, word_groups):
        """Run the given set of word groups through a set of filters to create
        passwords

        Parameters:
            word_groups (list): list of strings to be turned into passwords
        """

        def is_empty(string):
            return string.strip() == ""
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
                max_combo=4,
                min_length=4,
                max_length=15
            )

        # remove empty words again
        word_groups = remove_empty(word_groups)
        
        for word in word_groups:
            self._output.write("{}\n".format(word))
        
