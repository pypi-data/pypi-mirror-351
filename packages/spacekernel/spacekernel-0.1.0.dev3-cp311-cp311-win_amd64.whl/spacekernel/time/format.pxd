#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

from numpy cimport ndarray

from libc.time cimport tm, time_t

from spacekernel.datamodel cimport DTF

from numpy cimport float64_t, int64_t, npy_datetime


ctypedef float64_t jd_t
ctypedef float64_t epoch_t  # for julian and besselian epochs
ctypedef int64_t ptp_t
ctypedef int64_t unixtime_t
ctypedef npy_datetime datetime64_t


cdef extern from * nogil:
    """
    #if defined(_WIN32) || defined(WIN32)
        #define timegm _mkgmtime
    #endif
    """
    time_t timegm(tm *)

cdef extern from "<time.h>" nogil:
    time_t _mkgmtime(tm *)  # Windows version
    time_t timegm(tm *)  # Unix version (will be used if not Windows)

cpdef ndarray[int64_t, ndim=1] int64_from_datetime64(ndarray datetime64)
cpdef ndarray[datetime64_t, ndim=1] datetime64_from_int64(ndarray[int64_t, ndim=1] int64)
cdef DTF[:] c_dtf_from_datetime64(ndarray datetime64)
cdef int64_t[:] c_int64_from_dtf(DTF[:] dtf)
cdef int c_jd12_from_dtf(DTF[:] dtf, jd_t[:, :] jd12, str scale)
cdef int c_dtf_from_jd12(jd_t[:, :] jd12, DTF[:] dtf, str scale)
cpdef ndarray[jd_t, ndim=1] jd_from_jd12(ndarray[jd_t, ndim=2] jd12)
cpdef ndarray[jd_t, ndim=2] jd12_from_jd(ndarray[jd_t, ndim=1] jd)
cpdef ndarray[jd_t, ndim=1] mjd_from_jd(ndarray[jd_t, ndim=1] jd)
cpdef ndarray[jd_t, ndim=1] jd_from_mjd(ndarray[jd_t, ndim=1] mjd)
cpdef ndarray[epoch_t, ndim=1] byear_from_jd12(ndarray[jd_t, ndim=2] jd12)
cpdef ndarray[jd_t, ndim=2] jd12_from_byear(ndarray[epoch_t, ndim=1] byear)
cpdef ndarray[epoch_t, ndim=1] jyear_from_jd12(ndarray[jd_t, ndim=2] jd12)
cpdef ndarray[jd_t, ndim=2] jd12_from_jyear(ndarray[epoch_t, ndim=1] jyear)