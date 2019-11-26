from pydoc import locate

__all__ = [
    "CmdFlag",
    "CmdDefault",
    "CmdArgParser"
]

class CmdArg():
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

        if value != None:
            self.value = value
            self.is_set = True
            return True
        return False

class CmdFlag(CmdArg):
    """Information structure for command line flag descriptions, contains name 
    on construct and the value can later be set by the parser.

    Attributes:
        name (str): long form name of flag
        description (str): description of flag purpose
        default_value (any): default value of the flag to supply if none provided
            during parsing
        short_name (str): (default=None) optional short hand name of flag
        accepted_type (str): (default='bool') accepted type for value to be 
            read to flag, if set to bool then value will be set to true if 
            the flag simply exists
    """
    def __init__(self, name, description, default_value, short_name=None, accepted_type='bool'):
        self.name = name
        self.short_name = short_name
        self.description = description
        self.default_value = default_value
        self.accepted_type = accepted_type

        self.is_bool_flag = accepted_type == 'bool'

        self.value = None

        self.names = [ x for x in [ self.name, self.short_name ] if x != None ]

        self.is_set = False

    def __str__(self):
        return self.name

class CmdDefault(CmdArg):
    """A named default value, if there is a value given without an associated
    flag then it will be read into an object such as this

    Attributes:
        name (str): name of default value
        accepted_type(str): string name of the accepted type to be used for the
            default flag

    """
    def __init__(self, name, accepted_type='str'):
        self.name = name
        self.accepted_type = accepted_type 

        self.names = [ self.name ]

        self.is_set = False

class CmdArgParser:
    """Given a raw string of arguments from the command line, parse them and 
    set their values to the object

    Attributes:
        arg_string (str): argument string to parse
        cmd_flags (list(CmdFlag)): list of CmdFlags for reading values into
        default_flags (list(CmdDefault)): list of default flags to be read into,
            an attempt will be made to match given values to a matching default
            variable, but for the most part they will be used in the order given
    """

    FLAG_SHORT = "-"
    FLAG_LONG = "--"

    def __init__(self, arg_string, cmd_flags, default_flags=[]):
        self.text = arg_string
        self._cmd_flags = cmd_flags
        self._default_flags = default_flags
        
        self.flags = self._parse_arg_string(arg_string, self._cmd_flags, self._default_flags)

        self.flags = self._fill_default_flag_values(self.flags, self._cmd_flags)

    def _fill_default_flag_values(self, filled_flags, cmd_flags):
        """Fill any missing flag values with their given default value

        Paramters:
            filled_flags (dict): a flag:value dictionary given from _parse_arg_string
            cmd_flags (list(CmdFlag)): list of flags to have their values filled
                into the flag dict

        """
        for flag in cmd_flags:
            if not flag.name in filled_flags:
                filled_flags[flag.name] = flag.default_value

        return filled_flags

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
                if name in flag.names:
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

    def _parse_arg_string(self, arg_string, cmd_flags, default_flags):
        """Parse a given argument string and return the set properties

        Parameters:
            arg_string (str): argument string
            cmd_flags (list(CmdFlag)): list of command flags
            default_flags (list(CmdDefault)): list of default flags, will be used
                in order given with attempts to match given values

        Returns:
            dict: a dictionary containing the argument strings fields 
        """

        # skip the first token since it is the name of the script
        tokens = self._get_tokens(arg_string)[1:]

        flags = {}

        i = 0
        while i < len(tokens):
            flag_name = tokens[i]
            if i < len(tokens) - 1:
                value = tokens[i+1]
            else:
                value = ""

            flag = self._get_flag(flag_name, cmd_flags)
            
            # if the accepted type for the flag is bool, then the intended
            # behavior is to set it to true without passing a value since it
            # just exists
            if flag != None and flag.accepted_type == "bool":
                flag.set_value(True)

                flags[flag.name] = flag.value

                i += 1 
                continue

            # current flag is flag but value is also flag, set to true
            if flag != None and self._get_flag(value, cmd_flags):
                # check for error setting flag value
                if not flag.set_value(True):
                    flag_name = self._get_flag_name(flag_name)
                    raise Exception(
                        "No value given for {} but {} required".format(flag_name, flag.accepted_type))

                flags[flag.name] = flag.value

            # current flag is flag and next is value
            if flag != None and not self._get_flag(value, cmd_flags):
                # check for error setting flag value
                if not flag.set_value(value):
                    raise Exception(
                        "Given value for flag {} invalid, expected type {}".format(flag_name, flag.accepted_type))

                flags[flag.name] = flag.value

                # next value was eaten so skip over it on next loop
                i+=1
            
            # given flag is actually an in place value, read into default args,
            # if there is any available
            if flag == None:
                # if there are no args open then raise exception
                if all([ default.is_set for default in default_flags ]):
                    raise Exception(
                        "Unknown flag '{}'".format(flag_name))

                # get all default flags that aren't already set
                default_pool = [ default for default in default_flags if not default.is_set ]

                # attempt to set to default flags until one matches
                default_found = False
                for default in default_pool:
                    if default.set_value(flag_name):
                        flags[default.name] = flag_name

                        default_found = True
                        break 
                
                # if not matching default flag is found then raise exception
                if not default_found:
                    raise Exception(
                        "Unknown flag or Unusable value '{}'".format(flag_name))

            i += 1
        
        return flags



        
        
        