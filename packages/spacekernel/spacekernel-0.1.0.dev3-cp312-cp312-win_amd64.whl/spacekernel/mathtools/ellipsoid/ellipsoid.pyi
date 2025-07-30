#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

from numpy.typing import NDArray

class Ellipsoid:

    Re: float
    """Ellipsoid equatorial radius (in meters)"""

    f: float
    """Ellipsoid flattening factor"""


    def __init__(self, Re: float, f: float) -> None: ...

    def reduced_lat_from_geodetic_lat(self, geodetic_lat: float | NDArray) -> float | NDArray: ...

    def geodetic_lat_from_reduced_lat(self, reduced_lat: float | NDArray) -> float | NDArray: ...

    def enu(self, lat: float | NDArray, lon: float | NDArray) -> NDArray: ...

    def surf_pos_from_surf_coord(self, lat: float | NDArray, lon: float | NDArray) -> float | NDArray: ...

    def surf_coord_from_surf_pos(self, r_surf: NDArray) -> NDArray: ...

    def solve_reduced_lat_equation(self, r: NDArray) -> float | NDArray: ...

    def lla_from_pos(self, r: NDArray) -> NDArray: ...

    def pos_from_lla(self, lat: float | NDArray, lon: float | NDArray, alt: float | NDArray) -> NDArray: ...

    def surf_pos_of_ray_first_intersection(self, r_source: NDArray, u_ray: NDArray) -> NDArray: ...

    def aer_coords(self, r_target: NDArray, lat_obs: float, lon_obs: float, alt_obs: float) -> NDArray: ...