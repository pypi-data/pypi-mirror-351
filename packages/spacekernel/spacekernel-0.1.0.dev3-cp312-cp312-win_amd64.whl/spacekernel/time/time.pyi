#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

import pandas
from spacekernel.typing import DatetimeLike

from numpy.typing import NDArray


# ========== ========== ========== ========== ========== ========== Time
class Time:

    def __init__(self, data: DatetimeLike, scale: str = 'UTC', format: str | None = None) -> None: ...

    # ========== ========== ========== ========== ========== public methods
    @classmethod
    def range(cls, scale='UTC', **kwargs) -> Time: ...

    @property
    def steps(self) -> NDArray: ...

    def to_astropy(self) -> 'astropy.time.Time': ...

    def to_pandas(self) -> pandas.DatetimeIndex: ...

    @classmethod
    def now(cls) -> Time: ...

    def to_scale(self, scale: str) -> Time: ...

    @property
    def scale(self) -> str: ...

    @property
    def size(self) -> int: ...

    @property
    def tai(self) -> Time: ...

    @property
    def tt(self) -> Time: ...

    @property
    def ut1(self) -> Time: ...

    @property
    def utc(self) -> Time: ...

    # ---------- ---------- ---------- ---------- formats
    @property
    def jd12(self) -> NDArray: ...

    @property
    def jd(self) -> NDArray: ...

    @property
    def mjd(self) -> NDArray: ...

    @property
    def jyear(self) -> NDArray: ...

    @property
    def byear(self) -> NDArray: ...

    @property
    def dtf(self) -> NDArray: ...

    @property
    def datetime64(self) -> NDArray: ...

    @property
    def int64(self) -> NDArray: ...

    # ---------- ---------- ---------- ---------- scale related formats
    @property
    def unixtime(self) -> NDArray: ...

    @property
    def ptp(self) -> NDArray: ...

    # ---------- ---------- ---------- ---------- scale deltas
    @property
    def ut1_utc(self) -> NDArray: ...

    @property
    def ut1_tai(self) -> NDArray: ...

    @property
    def tt_ut1(self) -> NDArray: ...

    @property
    def tai_utc(self) -> NDArray: ...