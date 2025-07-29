import os
from .exceptions import ValidationError


class ArgparseCustomTypes:
    @staticmethod
    def dir_path(path_str):
        path_str = os.path.realpath(path_str)
        if not os.path.isdir(path_str):
            raise ValidationError(f"{path_str} is not a valid directory")
        return path_str
