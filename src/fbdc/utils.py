from os.path import abspath, join
from typing import Callable


def set_root(root: str) -> Callable[[str], str]:
    return lambda path: join(abspath(root), path)
