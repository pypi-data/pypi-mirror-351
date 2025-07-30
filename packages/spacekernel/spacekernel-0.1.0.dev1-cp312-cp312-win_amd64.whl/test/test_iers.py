#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

import numpy, pandas

from matplotlib import pyplot

from spacekernel.iers import BulletinA, BulletinC, update_bulletins, get_latest_update, EOP


class TestBulletinA:

    def test_update(self) -> None:

        BulletinA.path.unlink(missing_ok=True)

        BulletinA.update()

        assert BulletinA.path.is_file()

    def test_singleton(self) -> None:

        b1 = BulletinA()
        b2 = BulletinA()

        assert b1 is b2

    def test_data(self) -> None:
        print()

        bull = BulletinA()

        # ---------- ---------- ---------- ---------- date
        assert numpy.issubdtype(bull.mjd_utc.dtype, numpy.double)
        assert numpy.issubdtype(bull.jd12_utc.dtype, numpy.double)
        assert numpy.issubdtype(bull.jd12_ut1.dtype, numpy.double)
        assert numpy.issubdtype(bull.mjd_ut1.dtype, numpy.double)
        assert numpy.issubdtype(bull.date_utc.dtype, numpy.datetime64)

        # ---------- ---------- ---------- Polar motion
        assert numpy.issubdtype(bull.pm_pred.dtype, numpy.bool_)
        assert numpy.issubdtype(bull.pm_x.dtype, numpy.double)
        assert numpy.issubdtype(bull.pm_x_error.dtype, numpy.double)
        assert numpy.issubdtype(bull.pm_y.dtype, numpy.double)
        assert numpy.issubdtype(bull.pm_y_error.dtype, numpy.double)

        # ---------- ---------- ---------- dut = UT1 - UTC
        assert numpy.issubdtype(bull.dut_pred.dtype, numpy.bool_)
        assert numpy.issubdtype(bull.dut.dtype, numpy.double)
        assert numpy.issubdtype(bull.dut_error.dtype, numpy.double)

        # ---------- ---------- ---------- LOD
        assert numpy.issubdtype(bull.lod.dtype, numpy.double)
        assert numpy.issubdtype(bull.lod_error.dtype, numpy.double)

        # ---------- ---------- ---------- Nutation
        assert numpy.issubdtype(bull.nutation_pred.dtype, numpy.bool_)
        assert numpy.issubdtype(bull.dX_IAU2000A.dtype, numpy.double)
        assert numpy.issubdtype(bull.dX_IAU2000A_error.dtype, numpy.double)
        assert numpy.issubdtype(bull.dY_IAU2000A.dtype, numpy.double)
        assert numpy.issubdtype(bull.dY_IAU2000A_error.dtype, numpy.double)


class TestBulletinC:

    def test_update(self) -> None:

        BulletinC.path.unlink(missing_ok=True)

        BulletinC.update()

        assert BulletinC.path.is_file()

    def test_singleton(self) -> None:

        b1 = BulletinC()
        b2 = BulletinC()

        assert b1 is b2

    def test_data(self) -> None:
        print()

        bull = BulletinC()

        # ---------- ---------- ---------- ---------- date
        assert numpy.issubdtype(bull.mjd_utc.dtype, numpy.double)
        assert numpy.issubdtype(bull.jd12_utc.dtype, numpy.double)
        assert numpy.issubdtype(bull.jd12_ut1.dtype, numpy.double)
        assert numpy.issubdtype(bull.mjd_ut1.dtype, numpy.double)
        assert numpy.issubdtype(bull.date_utc.dtype, numpy.datetime64)

        # ---------- ---------- ---------- ---------- dat
        assert numpy.issubdtype(bull.dat.dtype, numpy.int64)


def test_update_bulletins() -> None:
    print()

    update_bulletins()

    assert (pandas.Timestamp.utcnow() - get_latest_update()).total_seconds() < 10.0


class TestEOP:

    def test_data(self) -> None:
        print()

        bullA = BulletinA()
        bullC = BulletinC()

        mjd_utc_A = bullA.mjd_utc

        mjd_utc = numpy.linspace(mjd_utc_A[0], mjd_utc_A[-1], 2000)

        eop = EOP(mjd_utc)

        fig, axes = pyplot.subplots(5, sharex=True)

        axes[0].plot(mjd_utc_A, bullA.pm_x, 'o')
        axes[0].plot(mjd_utc, eop.pm_x)

        axes[1].plot(mjd_utc_A, bullA.pm_y, 'o')
        axes[1].plot(mjd_utc, eop.pm_y)

        axes[2].plot(mjd_utc_A, bullA.dX_IAU2000A, 'o')
        axes[2].plot(mjd_utc, eop.dX)

        axes[3].plot(mjd_utc_A, bullA.dY_IAU2000A, 'o')
        axes[3].plot(mjd_utc, eop.dY)

        axes[4].plot(bullC.mjd_utc, bullC.dat, 'o')
        axes[4].plot(mjd_utc, eop.dat)

        pyplot.show()

