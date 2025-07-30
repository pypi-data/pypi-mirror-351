#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

from __future__ import annotations

from numpy import ndarray, datetime64, int64

import pandas
from datetime import datetime

from typing import TypeAlias, Iterator, TypeVar

from typing import Any


ScalarDatetimeLike = int | float | pandas.Timestamp | str | datetime

Time = TypeVar('spacekernel.Time')
aspy_Time = TypeVar('astropy.time.Time')

DatetimeLike: TypeAlias = ndarray[Any, datetime64 | int64] | pandas.DatetimeIndex | aspy_Time | Time | Iterator[ScalarDatetimeLike]
"""Alias representing types that can be coerced into :class:`smet.Time` objects"""