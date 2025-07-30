#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

from .time import Time

try:
    from importlib.metadata import version, PackageNotFoundError
    __version__ = version("spacekernel")
except PackageNotFoundError:
    __version__ = None