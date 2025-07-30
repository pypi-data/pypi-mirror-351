#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""


cdef inline void scale(const double scalar, const double[3] a, double[3] c) nogil

cdef inline void add(const double[3] a, const double[3] b, double[3] c) nogil

cdef inline void sub(const double[3] a, const double[3] b, double[3] c) nogil

cdef inline double dot(const double[3] a, const double[3] b) nogil

cdef inline void cross(const double[3] a, const double[3] b, double[3] c) nogil

cdef inline double norm(const double[3] a) nogil

cdef inline double angle(const double[3] a, const double[3] b) nogil

cdef inline void normalize(const double[3] a, double[3] u) nogil
