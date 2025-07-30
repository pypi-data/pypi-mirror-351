#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

import pandas

from test.orekit import Orekit


def propagate_tle(line1: str,
                  line2: str,
                  time: pandas.DatetimeIndex) -> pandas.DataFrame:
    """

    Parameters
    ----------
    line1 : str

    line2 : str

    time : pandas.DatetimeIndex

    Returns
    -------

    """

    with Orekit():

        from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
        from org.orekit.time import AbsoluteDate, TimeScalesFactory
        from org.orekit.frames import FramesFactory, Transform
        from org.orekit.utils import IERSConventions
        from org.orekit.bodies import GeodeticPoint
        from org.orekit.bodies import OneAxisEllipsoid
        from org.orekit.utils import Constants

        # ---------- ---------- ---------- ---------- ---------- ----------
        utc = TimeScalesFactory.getUTC()

        def absolutedate_from_timestamp(t: pandas.Timestamp) -> AbsoluteDate:
            return AbsoluteDate(t.year, t.month, t.day, t.hour, t.minute, t.second, utc)

        # ---------- ---------- ---------- ---------- ---------- propagator
        tle = TLE(line1, line2)
        propagator = TLEPropagator.selectExtrapolator(tle)

        # ---------- ---------- ---------- ---------- ---------- frames
        GCRF = FramesFactory.getGCRF()
        ITRF = FramesFactory.getITRF(IERSConventions.IERS_2010, True)

        # Define Earth ellipsoid (WGS84)
        earth = OneAxisEllipsoid(
            Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
            Constants.WGS84_EARTH_FLATTENING,
            ITRF
        )

        def lla(pv_ITRF):
            """Convert ITRF Cartesian coordinates to LLA."""
            # Create a GeodeticPoint from Cartesian coordinates
            gp = earth.transform(pv_ITRF.getPosition(),  # Input as list or Vector3D
                ITRF,  # Input frame
                None  # Optional date (None for ITRF)
            )

            return {
                'lon': gp.getLongitude(),
                'lat': gp.getLatitude(),
                'alt': gp.getAltitude()
            }

        # ---------- ---------- ---------- ---------- ---------- ----------
        results = []

        for t in time:
            abs_date = absolutedate_from_timestamp(t)

            # ---------- ---------- ---------- ---------- ---------- TEME
            state_TEME = propagator.propagate(abs_date)

            state_TEME_dict = {
                'rx_TEME': state_TEME.getPVCoordinates().getPosition().getX(),
                'ry_TEME': state_TEME.getPVCoordinates().getPosition().getY(),
                'rz_TEME': state_TEME.getPVCoordinates().getPosition().getZ(),
                'vx_TEME': state_TEME.getPVCoordinates().getVelocity().getX(),
                'vy_TEME': state_TEME.getPVCoordinates().getVelocity().getY(),
                'vz_TEME': state_TEME.getPVCoordinates().getVelocity().getZ(),
            }

            # ---------- ---------- ---------- ---------- ---------- GCRF
            transform = GCRF.getTransformTo(state_TEME.getFrame(), state_TEME.getDate())
            pv_GCRF = transform.transformPVCoordinates(state_TEME.getPVCoordinates())

            state_GCRF_dict = {
                'rx_GCRF': pv_GCRF.getPosition().getX(),
                'ry_GCRF': pv_GCRF.getPosition().getY(),
                'rz_GCRF': pv_GCRF.getPosition().getZ(),
                'vx_GCRF': pv_GCRF.getVelocity().getX(),
                'vy_GCRF': pv_GCRF.getVelocity().getY(),
                'vz_GCRF': pv_GCRF.getVelocity().getZ(),
            }

            # ---------- ---------- ---------- ---------- ---------- ITRF
            transform = ITRF.getTransformTo(state_TEME.getFrame(), state_TEME.getDate())
            pv_ITRF = transform.transformPVCoordinates(state_TEME.getPVCoordinates())

            state_ITRF_dict = {
                'rx_ITRF': pv_ITRF.getPosition().getX(),
                'ry_ITRF': pv_ITRF.getPosition().getY(),
                'rz_ITRF': pv_ITRF.getPosition().getZ(),
                'vx_ITRF': pv_ITRF.getVelocity().getX(),
                'vy_ITRF': pv_ITRF.getVelocity().getY(),
                'vz_ITRF': pv_ITRF.getVelocity().getZ(),
            }

            # ---------- ---------- ---------- ---------- ----------
            results.append(state_GCRF_dict | state_ITRF_dict | lla(pv_ITRF) | state_TEME_dict)

        # ---------- ---------- ---------- ---------- ---------- ----------
        return pandas.DataFrame(results, index=time)


if __name__ == '__main__':

    with Orekit():

        from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
        from org.orekit.time import AbsoluteDate, TimeScalesFactory

        # ISS TLE (replace with your own)
        tle_lines = [
            "1 25544U 98067A   24173.68657856  .00016717  00000-0  10270-3 0  9992",
            "2 25544  51.6416  32.4122 0003683  61.8532  82.5866 15.50170324448695"
        ]

        # Create TLE and propagator
        tle = TLE(tle_lines[0], tle_lines[1])
        propagator = TLEPropagator.selectExtrapolator(tle)

        # Propagate 1 hour ahead
        utc = TimeScalesFactory.getUTC()
        end_date = propagator.getInitialState().getDate().shiftedBy(3600.0)  # 1 hour later
        final_state = propagator.propagate(end_date)

        print(f"ISS Position after 1h: {final_state.getPVCoordinates().getPosition()}")
        print(f"ISS Velocity after 1h: {final_state.getPVCoordinates().getVelocity()}")