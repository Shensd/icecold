class CmdArgParser:
    """Given a raw string of arguments from the command line, parse them and 
    set their values to the object

    Attributes:
        arg_string (str): argument string to parse

    """

    FLAG_SHORT = "-"
    FLAG_LONG = "--"

    def __init__(self, arg_string):
        self.text = arg_string
        self.flags = self._parse_arg_string(arg_string)

    def _get_tokens(self, arg_string):
        """Get the tokens of an argument string

        Parameters:
            arg_string (str): argument string 

        Returns:
            list (str): string tokens
        """

        return arg_string.split(" ")

    def _is_flag(self, token):
        """Returns if a given token is an argument flag

        Parameteres:
            token (str): token to test

        Returns:
            bool: true if a argument flag, otherwise false
        """

        return token.startswith(self.FLAG_LONG) or token.startswith(self.FLAG_SHORT)

    def _get_flag_name(self, flag):
        """Get the name of a provided flag, if provided flag does not have flag 
        structure (starts with hyphen), then the original text will be returned

        Parameters:
            flag (str): command flag to get name of

        Returns:
            str: name of flag, or original flag text if not flag form
        """

        for i in range(0, len(flag)):
            if flag[i] != '-':
                return flag[(i):]
        return flag

    def _parse_arg_string(self, arg_string):
        """Parse a given argument string and return the set properties

        Parameters:
            arg_string (str): argument string

        Returns:
            dict: a dictionary containing the argument strings fields 
        """

        # skip the first token since it is the name of the script
        tokens = self._get_tokens(arg_string)[1:]
        fields = {}

        for i in range(0, len(tokens)):
            flag = tokens[i]
            if i < len(tokens) - 1:
                value = tokens[i+1]
            else:
                value = ""

            if self._is_flag(flag):
                fields[self._get_flag_name(flag)] = value
            if not self._is_flag(value):
                # next value eaten, skip over it
                i += 1
        
        return fields



        
        
        