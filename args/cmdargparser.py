from pydoc import locate

class CmdFlag(dict):
    """Information structure for command line flag descriptions, contains name 
    on construct and the value can later be set by the parser.

    Attributes:
        name (str): long form name of flag
        description (str): description of flag purpose
        short_name (str): (default=None) optional short hand name of flag
        accepted_type (str): (default='bool') accepted type for value to be 
            read to flag, if set to bool then value will be set to true if 
            the flag simply exists
    """
    def __init__(self, name, description, short_name=None, accepted_type='bool'):
        self.name = name
        self.short_name = short_name
        self.description = description
        self.accepted_type = accepted_type

        self.is_bool_flag = accepted_type == 'bool'

        self.value = None


    def _try_cast(self, value, typename):
        """Attempt to cast a value to the given typename, returns the converted
        value on success

        Parameters:
            value (any): value to attempt to convert
            typename (str): name of type to attempt to conver to

        Returns:
            any or None: returns converted value on success, None on failure
        """

        translator = locate(typename)

        try:
            converted = translator(value)
            return converted
        except:
            return None

    def set_value(self, value):
        """Set the flag's value to the given value, if the given value's type 
        does not match the requested type then an exception is raised

        Parameters:
            value (any): value to be set to flag

        Returns:
            bool: True on success, False on failure
        """
        value = self._try_cast(value, self.accepted_type)

        if type(value) == self.accepted_type:
            self.value = value
            return True
        return False
    
    def __len__(self):
        return int(self.value != None)

    def __getitem__(self, key):
        if key == "value":
            return self.value
        if key == self.name or key == self.short_name:
            return True
        return None

    def __setitem__(self, key, value):
        if key == "value":
            self.set_value(value)

    def __iter__(self):
        if self.short_name:
            return [ self.name, self.short_name ]
        return [ self.name ]

class CmdArgParser:
    """Given a raw string of arguments from the command line, parse them and 
    set their values to the object

    Attributes:
        arg_string (str): argument string to parse
        cmd_flags (list(CmdFlag)): list of CmdFlags for reading values into
    """

    FLAG_SHORT = "-"
    FLAG_LONG = "--"

    def __init__(self, arg_string, cmd_flags):
        self.text = arg_string
        self.flags = cmd_flags
        
        self._parse_arg_string(arg_string, cmd_flags)

    def _get_tokens(self, arg_string):
        """Get the tokens of an argument string

        Parameters:
            arg_string (str): argument string 

        Returns:
            list (str): string tokens
        """

        return arg_string.split(" ")

    def _get_flag(self, token, cmd_flags):
        """Returns the CmdFlag if the given token can be resolved to one, 
        otherwise None will be returned

        Parameteres:
            token (str): token to test
            cmd_flags (list(CmdFlag)): list of accepted flags

        Returns:
            CmdFlag or None: CmdFlag if found, otherwise Nonetype returned
        """

        if token.startswith(self.FLAG_LONG) or token.startswith(self.FLAG_SHORT):
            name = self._get_flag_name(token)

            for flag in cmd_flags:
                if name in flag:
                    return flag

        return None

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

    def _parse_arg_string(self, arg_string, cmd_flags):
        """Parse a given argument string and return the set properties

        Parameters:
            arg_string (str): argument string
            cmd_flags (list(CmdFlag)): list of command flags

        Returns:
            dict: a dictionary containing the argument strings fields 
        """

        # skip the first token since it is the name of the script
        tokens = self._get_tokens(arg_string)[1:]

        for i in range(0, len(tokens)):
            flag_name = tokens[i]
            if i < len(tokens) - 1:
                value = tokens[i+1]
            else:
                value = ""

            flag = self._get_flag(flag_name, cmd_flags)

            # current flag is flag but value is also flag, set to true
            if flag and self._get_flag(value, cmd_flags):

                # check for error setting flag value
                if not flag.set_value(True):
                    flag_name = self._get_flag_name(flag_name)
                    raise Exception(
                        "No value given for {} but {} required".format(flag_name, flag.accepted_type))

            # current flag is flag and next is value
            if flag and not self._get_flag(value, cmd_flags):
                
                # check for error setting flag value
                if not flag.set_value(value):
                    raise Exception(
                        "Given value for flag {} invalid, expected type {}".format(flag_name, flag.accepted_type))

                # next value was eaten so skip over it on next loop
                i+=1
        
        return cmd_flags



        
        
        