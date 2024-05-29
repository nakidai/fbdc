"""Just some useful utils"""

from os.path import abspath, join
from typing import Callable


def set_root(root: str) -> Callable[[str], str]:
    """
    :return: Returns function that joins path to path which is argument of this function
    """

    return lambda path: join(abspath(root), path)
