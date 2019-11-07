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

        def is_empty(string):
            return string.strip() == ""

        word_groups = [word for word in word_groups if not is_empty(word)]

        for word in word_groups:
            self._output.write(word)
        