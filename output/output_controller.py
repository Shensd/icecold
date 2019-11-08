import os
import stat

class OutputController:
    """Buffer for writing to disk or to standard out

    Attributes:
        file_location (str): location to write to on disk, this argument
            is ignored if standard_out is set to True
        standard_out (bool): (default=False) if set to true then all given 
            input is written to standard out (command line)
    """

    def __init__(self, file_location, standard_out=False):
        self.file_location = file_location
        self._stdout = standard_out

        if not standard_out:
            self._file_descriptor = self._try_open(file_location)

    def write(self, line):
        """Write to the output

        Parameters:
            line (str): line to write to output stream
        """
        if self._stdout:
            print(line, end="")
        else:
            self._file_descriptor.write(line)

    def _have_permissions(self, location):
        """Return true if there is sufficient permissions to write to the given
        location

        Parameters:
            location (str): path to desired location
        
        Returns:
            bool: true if sufficient permissions, otherwise false
        """
        stats = os.stat(location)
        # check specifically for write permission
        return bool(stats.st_mode & stat.S_IWUSR)

    def _try_open(self, location):
        """Try to open the given file, returns a descriptor on success, otherwise
        raises an error with the corresponding issue 

        Parameters:
            location (str): path to desired location

        Returns:
            file-like: returns a descriptor on success 

        """
        if self._have_permissions(location):
            return open(location, 'w')

        raise Exception(
            "You do not have permissions to write to given location '{}'".format(location)
        )