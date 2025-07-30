#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

from spacekernel.time cimport jd_t


cdef class Time:

    cdef:
        Py_ssize_t[2] shape
        Py_ssize_t[2] strides
        Py_ssize_t length
        str _scale  # should this be changed to bytes?
        bint _is_scalar
        jd_t[:, :] _jd12  # SOFA internal format