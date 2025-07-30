#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

import numpy

from matplotlib import pyplot

from spacekernel.time import Time

from line_profiler import LineProfiler

from spacekernel.propagators.analytical.sgp4 import propagate_tle as propagate_tle_sk, TLE
from test.orekit.propagation import propagate_tle as propagate_tle_ok

from test import profile


@profile
def test_tle_propagation():
    # MOLNIYA 2-9
    line1 = '1  7276U 74026A   25145.84713414  .00000013  00000-0  00000+0 0  9993'
    line2 = '2  7276  64.3566  79.2896 6584676 266.9325  21.8190  2.45096989275692'

    time = Time.range(start='2025-05-28', end='2025-05-30', step=30)

    # ---------- ---------- ---------- ---------- ---------- orekit
    time_pd = time.to_pandas()
    frame = propagate_tle_ok(line1, line2, time_pd)
    r_ok = frame[['rx_TEME', 'ry_TEME', 'rz_TEME']].values
    v_ok = frame[['vx_TEME', 'vy_TEME', 'vz_TEME']].values

    # ---------- ---------- ---------- ---------- ---------- spacekernel
    tle = TLE(line1, line2)
    r_sk, v_sk = propagate_tle_sk(time, tle)

    # ---------- ---------- ---------- ---------- ---------- ----------
    try:
        assert numpy.allclose(r_sk, r_ok, rtol=0.0, atol=1.000) # < 1.000 m
        assert numpy.allclose(v_sk, v_ok, rtol=0.0, atol=0.001) # < 0.001 m/s
    except AssertionError as error:

        figure, axes = pyplot.subplots(2, sharex=True)

        dr = r_sk - r_ok

        axes[0].plot(time.datetime64, dr[:, 0], label='x')
        axes[0].plot(time.datetime64, dr[:, 1], label='y')
        axes[0].plot(time.datetime64, dr[:, 2], label='z')
        axes[0].plot(time.datetime64, numpy.linalg.norm(dr, axis=1), label='norm', linestyle='--')

        dv = v_sk - v_ok

        axes[1].plot(time.datetime64, dv[:, 0])
        axes[1].plot(time.datetime64, dv[:, 1])
        axes[1].plot(time.datetime64, dv[:, 2])
        axes[1].plot(time.datetime64, numpy.linalg.norm(dv, axis=1),  linestyle='--')

        figure.legend()

        pyplot.show()

        raise error


class TestTLE:

    def test_instantiates(self):
        print()
        line1 = '1  7276U 74026A   25145.84713414  .00000013  00000-0  00000+0 0  9993'
        line2 = '2  7276  64.3566  79.2896 6584676 266.9325  21.8190  2.45096989275692'

        tle = TLE(line1, line2)

        print(line1)
        print(line2)

        print(tle.satno)

        print(tle.epoch)
