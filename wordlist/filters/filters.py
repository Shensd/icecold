class Filter:
    def filter_words(self, word_groups):
        return word_groups

class FilterNoCaps(Filter):
    """
    Removes capitals from word groups
    """
    def filter_words(self, word_groups):
        return [ word.lower() for word in word_groups ]

class FilterNoSymbols(Filter):
    """
    Removes characters considered symbols, these are:

    ~`!@#$%^&*()-_=+[{}]\|'";:/?.>,<

    """
    def filter_words(self, word_groups):
        symbols = "~`!@#$%^&*()-_=+[{\}]\\|'\";:/?.>,<"

        
