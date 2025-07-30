#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

from numpy.typing import NDArray


class EOP:

    def __init__(self, mjd_utc: NDArray) -> None: ...

    @classmethod
    def get_TT_UT1_from_mjd_ut1(cls, mjd_ut1: NDArray) -> NDArray: ...

    @property
    def pm_x(self) -> NDArray: ...

    @property
    def pm_y(self) -> NDArray: ...

    @property
    def lod(self) -> NDArray: ...

    @property
    def dX(self) -> NDArray: ...

    @property
    def dY(self) -> NDArray: ...

    @property
    def dat(self) -> NDArray: ...

    @property
    def TAI_UT1(self) -> NDArray: ...

    @property
    def TT_UT1(self) -> NDArray: ...