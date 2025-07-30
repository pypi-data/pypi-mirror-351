#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

from spacekernel.datamodel cimport SurfCoord, ENU_Frame, LLA, AER


cdef class Ellipsoid:

    cdef:
        readonly double Re, f, Rp

    cdef inline double c_reduced_lat_from_geodetic_lat(self, const double geodetic_lat) nogil

    cdef inline double c_geodetic_lat_from_reduced_lat(self, const double reduced_lat) nogil

    cdef void surf_normal_vector(self, const SurfCoord point, double * u_normal) nogil

    cdef void surf_tangent_vector(self, const SurfCoord point, double * u_east, double * u_north) nogil

    cdef void c_enu(self, const SurfCoord point, ENU_Frame * enu) nogil

    cdef void c_surf_pos_from_surf_coord(self, const SurfCoord point, double[3] r_surf) nogil

    cdef void c_surf_coord_from_surf_pos(self, const double[3] r_surf, SurfCoord * point) nogil

    cdef double c_solve_reduced_lat_equation(self, const double[3] r) nogil

    cdef void c_lla_from_pos(self, const double[3] r, LLA * lla) nogil

    cdef void c_pos_from_lla(self, const LLA lla, double[3] r) nogil

    cdef void c_surf_pos_of_ray_first_intersection(self, const double[3] r_ray, const double[3] u_ray, double[3] r_surf) nogil

    cdef void c_aer_coords(self, const double[3] r_target, const LLA lla_obs, AER * aer) nogil