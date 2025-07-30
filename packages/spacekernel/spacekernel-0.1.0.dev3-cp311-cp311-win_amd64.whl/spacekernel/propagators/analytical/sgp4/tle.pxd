#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

from spacekernel.time cimport Time


cdef packed struct _TLE:
    char[69] line1
    char[69] line2


cdef class TLE:

    cdef:
        char[70] _line1
        char[70] _line2
        bint strict_validation

        char[6] _satno

        readonly Time epoch

    cdef void parse_line1(self)