#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

from spacekernel.time.format cimport jd_t

cdef int c_tt_from_ut1(jd_t[:, :] jd12_ut1, double[:] TT_UT1, jd_t[:, :] jd12_tt) except -1 nogil
cdef int c_ut1_from_tt(jd_t[:, :] jd12_tt, double[:] TT_UT1, jd_t[:, :] jd12_ut1) except -1 nogil

cdef int c_tai_from_tt(jd_t[:, :] jd12_tt, jd_t[:, :] jd12_tai) except -1 nogil
cdef int c_tt_from_tai(jd_t[:, :] jd12_tai, jd_t[:, :] jd12_tt) except -1 nogil

cdef int c_utc_from_tai(jd_t[:, :] jd12_tai, jd_t[:, :] jd12_utc) except -1 nogil
cdef int c_tai_from_utc(jd_t[:, :] jd12_utc, jd_t[:, :] jd12_tai) except -1 nogil

cdef int c_ut1_from_utc(jd_t[:, :] jd12_utc, double[:] dut1, jd_t[:, :] jd12_ut1) except -1 nogil
cdef int c_utc_from_ut1(jd_t[:, :] jd12_ut1, double[:] dut1, jd_t[:, :] jd12_utc) except -1 nogil
