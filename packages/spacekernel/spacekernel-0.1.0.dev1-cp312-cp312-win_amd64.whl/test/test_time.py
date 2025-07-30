#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

import numpy
import pandas
import pytest
from astropy.time import Time as Time_

from pandas._libs.tslibs.fields import get_date_field

from matplotlib import pyplot

from spacekernel.time import datetime64_from_int64, int64_from_datetime64
from spacekernel.time import dtf_from_datetime64
from spacekernel.time import int64_from_dtf
from spacekernel.time import jd12_from_dtf, dtf_from_jd12
from spacekernel.time import jd12_from_jd, jd_from_jd12
from spacekernel.time import byear_from_jd12, jd12_from_byear
from spacekernel.time import jyear_from_jd12, jd12_from_jyear

from spacekernel.time import tt_from_tai, tai_from_tt
from spacekernel.time import utc_from_tai, tai_from_utc
from spacekernel.time import ut1_from_utc, utc_from_ut1

from spacekernel.time import Time

from test import profile

# ---------- ---------- ---------- ---------- ---------- ----------
from line_profiler import LineProfiler

# ---------- ---------- ---------- ---------- ---------- ----------
from numpy.typing import NDArray


class TimeTypes:

    def __init__(self, int64):
        self.int64 = int64

    @property
    def datetime64(self):
        try:
            return self.__datetime64

        except AttributeError:
            self.__datetime64 = self.int64.astype('datetime64[ns]')

            return self.__datetime64

    @property
    def dtf(self):
        """datetime fields"""

        # datetime64 = self.datetime64
        #
        # year = datetime64.astype('datetime64[Y]').astype(int) + 1970
        # month = datetime64.astype('datetime64[M]').astype(int) % 12 + 1
        # day = (datetime64.astype('datetime64[D]') - datetime64.astype('datetime64[M]')).astype(int) + 1
        # hour = (datetime64.astype('datetime64[h]') - datetime64.astype('datetime64[D]')).astype(int)
        # minute = (datetime64.astype('datetime64[m]') - datetime64.astype('datetime64[h]')).astype(int)
        # second = (datetime64.astype('datetime64[ns]') - datetime64.astype('datetime64[m]')).astype(int) / 1e9

        year = get_date_field(self.int64, 'Y')
        month = get_date_field(self.int64, 'M')
        day = get_date_field(self.int64, 'D')
        hour = get_date_field(self.int64, 'h')
        minute = get_date_field(self.int64, 'm')
        second = get_date_field(self.int64, 's')
        us = get_date_field(self.int64, 'us')
        ns = get_date_field(self.int64, 'ns')
        second = 1.0*second + us*1e-6 + ns*1e-9

        dtype = [
            ('year', numpy.uint16),
            ('month', numpy.uint8),
            ('day', numpy.uint8),
            ('hour', numpy.uint8),
            ('minute', numpy.uint8),
            ('second', numpy.double)
        ]

        _dtf = numpy.zeros(shape=(len(year),), dtype=dtype)

        _dtf['year'] = year
        _dtf['month'] = month
        _dtf['day'] = day
        _dtf['hour'] = hour
        _dtf['minute'] = minute
        _dtf['second'] = second

        return _dtf

    @property
    def DatetimeIndex(self):
        try:
            return self.__DatetimeIndex

        except AttributeError:
            self.__DatetimeIndex = pandas.to_datetime(self.int64)

            return self.__DatetimeIndex

    @property
    def datetime(self):
        try:
            return self.__datetime

        except AttributeError:
            self.__datetime = self.DatetimeIndex.to_pydatetime()

            return self.__datetime

    @property
    def astropy(self):
        try:
            return self.__astropy

        except AttributeError:
            self.__astropy = Time_(self.datetime64, format='datetime64',
                                   precision=9)

            return self.__astropy

    @property
    def jd12(self):

        return numpy.hstack([
            self.astropy.jd1.reshape(-1, 1),
            self.astropy.jd2.reshape(-1, 1)
        ])

    @property
    def jd(self):
        return self.jd12[:, 0] + self.jd12[:, 1]

    @property
    def mjd(self):
        return self.jd12[:, 0] + self.jd12[:, 1] - 2_400_000.5

    @property
    def byear(self):
        return self.astropy.byear

    @property
    def jyear(self):
        return self.astropy.jyear

    @property
    def str(self):
        try:
            return self.__str

        except AttributeError:
            self.__str = [str(t) for t in self.DatetimeIndex]

            return self.__str

    @property
    def DatetimeIndex_utc(self):
        try:
            return self.__DatetimeIndex_utc

        except AttributeError:

            self.__DatetimeIndex_utc = self.DatetimeIndex.tz_localize('utc')

            return self.__DatetimeIndex_utc

    @property
    def DatetimeIndex_non_utc(self):
        try:
            return self.__DatetimeIndex_non_utc

        except AttributeError:

            self.__DatetimeIndex_non_utc = self.DatetimeIndex_utc.tz_convert('America/Sao_Paulo')

            return self.__DatetimeIndex_non_utc

    @property
    def str_utc(self):
        try:
            return self.__str_utc

        except AttributeError:

            self.__str_utc = [str(t) for t in self.DatetimeIndex_utc]

            return self.__str_utc

    @property
    def str_non_utc(self):
        try:
            return self.__str_non_utc

        except AttributeError:

            self.__str_non_utc = [str(t) for t in self.DatetimeIndex_non_utc]

            return self.__str_non_utc

    @property
    def datetime_utc(self):
        try:
            return self.__datetime_utc

        except AttributeError:

            self.__datetime_utc = self.DatetimeIndex_utc.to_pydatetime()

            return self.__datetime_utc

    @property
    def datetime_non_utc(self):
        try:
            return self.__datetime_non_utc

        except AttributeError:

            self.__datetime_non_utc = self.DatetimeIndex_non_utc.to_pydatetime()

            return self.__datetime_non_utc

    @classmethod
    def create_data(cls, N):
        # t = pandas.date_range(start='2021-03-18 14:20:03.596', freq='15351381384N', periods=N)

        t = pandas.date_range(start='2012-03-18 14:20:03.564957842',
                              end='2022-10-18 17:34:57.123456789', periods=N)

        return cls(int64=t.values.astype('int64'))


# ========== ========== ========== ========== ========== ==========
class TestFormatConversions:

    @pytest.fixture
    def time_1e3(self):
        return TimeTypes.create_data(1000)

    @pytest.fixture
    def time_1e6(self):
        return TimeTypes.create_data(1_000_000)

    # ---------- ---------- ---------- ---------- int64 -> datetime64
    def test_datetime64_from_int64(self, time_1e3):

        datetime64_ref = time_1e3.datetime64
        datetime64_spacekernel = datetime64_from_int64(time_1e3.int64)

        assert numpy.all(datetime64_ref == datetime64_spacekernel)

    # ---------- ---------- ---------- ---------- datetime64 -> int64
    def test_int64_from_datetime64(self, time_1e3):

        int64_ref = time_1e3.int64
        int64_spacekernel = int64_from_datetime64(time_1e3.datetime64)

        assert numpy.all(int64_ref == int64_spacekernel)

    # ---------- ---------- ---------- ---------- datetime64 -> dtf
    def test_dtf_from_datetime64(self, time_1e3):

        dtf_ref = time_1e3.dtf
        dtf_spacekernel = dtf_from_datetime64(time_1e3.datetime64)


        try:
            assert numpy.all(dtf_spacekernel['year'] == dtf_ref['year'])
            assert numpy.all(dtf_spacekernel['month'] == dtf_ref['month'])
            assert numpy.all(dtf_spacekernel['day'] == dtf_ref['day'])
            assert numpy.all(dtf_spacekernel['hour'] == dtf_ref['hour'])
            assert numpy.all(dtf_spacekernel['minute'] == dtf_ref['minute'])
            assert numpy.allclose(dtf_spacekernel['second'], dtf_ref['second'])

        except:

            figure, axes = pyplot.subplots(6, sharex=True)

            axes[0].plot(dtf_spacekernel['year'] - dtf_ref['year'])
            axes[1].plot(dtf_spacekernel['month'] - dtf_ref['month'])
            axes[2].plot(dtf_spacekernel['day'] - dtf_ref['day'])
            axes[3].plot(dtf_spacekernel['hour'] - dtf_ref['hour'])
            axes[4].plot(dtf_spacekernel['minute'] - dtf_ref['minute'])
            axes[5].plot(dtf_spacekernel['second'] - dtf_ref['second'])

            pyplot.show()

    # ---------- ---------- ---------- ---------- dtf -> int64
    def test_int64_from_dtf(self, time_1e3):

        int64_ref = time_1e3.int64
        int64_spacekernel = int64_from_dtf(time_1e3.dtf)

        try:
            assert numpy.all(int64_spacekernel == int64_ref)

        except:

            figure, axes = pyplot.subplots(2, sharex=True)

            axes[0].plot(int64_ref)
            axes[0].plot(int64_spacekernel)

            axes[1].plot(int64_ref - int64_spacekernel)

            pyplot.show()

    # ---------- ---------- ---------- ---------- dtf -> jd12
    def test_jd12_from_dtf(self, time_1e3):

        datetime64 = time_1e3.datetime64

        # ---------- ---------- ---------- ---------- utc
        scale = 'utc'
        aspy_time = Time_(datetime64, format='datetime64', scale=scale)

        jd_ref = aspy_time.jd1 + aspy_time.jd2
        jd_spacekernel = jd12_from_dtf(time_1e3.dtf, scale).sum(axis=1)

        try:
            assert numpy.all(jd_spacekernel == jd_ref)
            # assert numpy.allclose(jd_spacekernel, jd_ref)

        except AssertionError as error:

            figure, axes = pyplot.subplots(2, sharex=True)

            figure.suptitle(f'Problem in {scale}')
            axes[0].plot(jd_ref)
            axes[0].plot(jd_spacekernel)

            axes[1].plot(jd_ref - jd_spacekernel)

            pyplot.show()

            raise error

        # ---------- ---------- ---------- ---------- tai
        scale = 'tai'
        aspy_time = Time_(datetime64, format='datetime64', scale=scale)

        jd_ref = aspy_time.jd1 + aspy_time.jd2
        jd_spacekernel = jd12_from_dtf(time_1e3.dtf, scale).sum(axis=1)

        try:
            assert numpy.all(jd_spacekernel == jd_ref)
            # assert numpy.allclose(jd_spacekernel, jd_ref)

        except AssertionError as error:

            figure, axes = pyplot.subplots(2, sharex=True)

            figure.suptitle(f'Problem in {scale}')
            axes[0].plot(jd_ref)
            axes[0].plot(jd_spacekernel)

            axes[1].plot(jd_ref - jd_spacekernel)

            pyplot.show()

            raise error

        # ---------- ---------- ---------- ---------- ut1
        scale = 'ut1'
        aspy_time = Time_(datetime64, format='datetime64', scale=scale)

        jd_ref = aspy_time.jd1 + aspy_time.jd2
        jd_spacekernel = jd12_from_dtf(time_1e3.dtf, scale).sum(axis=1)

        try:
            assert numpy.all(jd_spacekernel == jd_ref)
            # assert numpy.allclose(jd_spacekernel, jd_ref)

        except AssertionError as error:

            figure, axes = pyplot.subplots(2, sharex=True)

            figure.suptitle(f'Problem in {scale}')
            axes[0].plot(jd_ref)
            axes[0].plot(jd_spacekernel)

            axes[1].plot(jd_ref - jd_spacekernel)

            pyplot.show()

            raise error

        # ---------- ---------- ---------- ---------- tt
        scale = 'tt'
        aspy_time = Time_(datetime64, format='datetime64', scale=scale)

        jd_ref = aspy_time.jd1 + aspy_time.jd2
        jd_spacekernel = jd12_from_dtf(time_1e3.dtf, scale).sum(axis=1)

        try:
            assert numpy.all(jd_spacekernel == jd_ref)
            # assert numpy.allclose(jd_spacekernel, jd_ref)

        except AssertionError as error:

            figure, axes = pyplot.subplots(2, sharex=True)

            figure.suptitle(f'Problem in {scale}')
            axes[0].plot(jd_ref)
            axes[0].plot(jd_spacekernel)

            axes[1].plot(jd_ref - jd_spacekernel)

            pyplot.show()

            raise error

    # ---------- ---------- ---------- ---------- jd12 -> dtf
    def test_dtf_from_jd12(self, time_1e3):

        datetime64 = time_1e3.datetime64
        dtf_ref = time_1e3.dtf

        # ---------- ---------- ---------- ---------- utc
        scale = 'utc'
        aspy_time = Time_(datetime64, format='datetime64', scale=scale)

        jd12 = numpy.hstack([
            aspy_time.jd1.reshape(-1, 1),
            aspy_time.jd2.reshape(-1, 1)
        ])

        dtf_spacekernel = dtf_from_jd12(jd12, scale)

        try:
            assert numpy.all(dtf_spacekernel['year'] == dtf_ref['year'])
            assert numpy.all(dtf_spacekernel['month'] == dtf_ref['month'])
            assert numpy.all(dtf_spacekernel['day'] == dtf_ref['day'])
            assert numpy.all(dtf_spacekernel['hour'] == dtf_ref['hour'])
            assert numpy.all(dtf_spacekernel['minute'] == dtf_ref['minute'])
            assert numpy.allclose(dtf_spacekernel['second'], dtf_ref['second'])

        except AssertionError as error:

            figure, axes = pyplot.subplots(6, sharex=True)

            figure.suptitle(f'Problem in {scale}')

            axes[0].plot(dtf_spacekernel['year'] - dtf_ref['year'])
            axes[1].plot(dtf_spacekernel['month'] - dtf_ref['month'])
            axes[2].plot(dtf_spacekernel['day'] - dtf_ref['day'])
            axes[3].plot(dtf_spacekernel['hour'] - dtf_ref['hour'])
            axes[4].plot(dtf_spacekernel['minute'] - dtf_ref['minute'])
            axes[5].plot(dtf_spacekernel['second'] - dtf_ref['second'])

            pyplot.show()

            raise error

        # ---------- ---------- ---------- ---------- tai
        scale = 'tai'
        aspy_time = Time_(datetime64, format='datetime64', scale=scale)

        jd12 = numpy.hstack([
            aspy_time.jd1.reshape(-1, 1),
            aspy_time.jd2.reshape(-1, 1)
        ])

        dtf_spacekernel = dtf_from_jd12(jd12, scale)

        try:
            assert numpy.all(dtf_spacekernel['year'] == dtf_ref['year'])
            assert numpy.all(dtf_spacekernel['month'] == dtf_ref['month'])
            assert numpy.all(dtf_spacekernel['day'] == dtf_ref['day'])
            assert numpy.all(dtf_spacekernel['hour'] == dtf_ref['hour'])
            assert numpy.all(dtf_spacekernel['minute'] == dtf_ref['minute'])
            assert numpy.allclose(dtf_spacekernel['second'], dtf_ref['second'])

        except AssertionError as error:

            figure, axes = pyplot.subplots(6, sharex=True)

            figure.suptitle(f'Problem in {scale}')

            axes[0].plot(dtf_spacekernel['year'] - dtf_ref['year'])
            axes[1].plot(dtf_spacekernel['month'] - dtf_ref['month'])
            axes[2].plot(dtf_spacekernel['day'] - dtf_ref['day'])
            axes[3].plot(dtf_spacekernel['hour'] - dtf_ref['hour'])
            axes[4].plot(dtf_spacekernel['minute'] - dtf_ref['minute'])
            axes[5].plot(dtf_spacekernel['second'] - dtf_ref['second'])

            pyplot.show()

            raise error

        # ---------- ---------- ---------- ---------- ut1
        scale = 'ut1'
        aspy_time = Time_(datetime64, format='datetime64', scale=scale)

        jd12 = numpy.hstack([
            aspy_time.jd1.reshape(-1, 1),
            aspy_time.jd2.reshape(-1, 1)
        ])

        dtf_spacekernel = dtf_from_jd12(jd12, scale)

        try:
            assert numpy.all(dtf_spacekernel['year'] == dtf_ref['year'])
            assert numpy.all(dtf_spacekernel['month'] == dtf_ref['month'])
            assert numpy.all(dtf_spacekernel['day'] == dtf_ref['day'])
            assert numpy.all(dtf_spacekernel['hour'] == dtf_ref['hour'])
            assert numpy.all(dtf_spacekernel['minute'] == dtf_ref['minute'])
            assert numpy.allclose(dtf_spacekernel['second'], dtf_ref['second'])

        except AssertionError as error:

            figure, axes = pyplot.subplots(6, sharex=True)

            figure.suptitle(f'Problem in {scale}')

            axes[0].plot(dtf_spacekernel['year'] - dtf_ref['year'])
            axes[1].plot(dtf_spacekernel['month'] - dtf_ref['month'])
            axes[2].plot(dtf_spacekernel['day'] - dtf_ref['day'])
            axes[3].plot(dtf_spacekernel['hour'] - dtf_ref['hour'])
            axes[4].plot(dtf_spacekernel['minute'] - dtf_ref['minute'])
            axes[5].plot(dtf_spacekernel['second'] - dtf_ref['second'])

            pyplot.show()

            raise error

        # ---------- ---------- ---------- ---------- tt
        scale = 'tt'
        aspy_time = Time_(datetime64, format='datetime64', scale=scale)

        jd12 = numpy.hstack([
            aspy_time.jd1.reshape(-1, 1),
            aspy_time.jd2.reshape(-1, 1)
        ])

        dtf_spacekernel = dtf_from_jd12(jd12, scale)

        try:
            assert numpy.all(dtf_spacekernel['year'] == dtf_ref['year'])
            assert numpy.all(dtf_spacekernel['month'] == dtf_ref['month'])
            assert numpy.all(dtf_spacekernel['day'] == dtf_ref['day'])
            assert numpy.all(dtf_spacekernel['hour'] == dtf_ref['hour'])
            assert numpy.all(dtf_spacekernel['minute'] == dtf_ref['minute'])
            assert numpy.allclose(dtf_spacekernel['second'], dtf_ref['second'])

        except AssertionError as error:

            figure, axes = pyplot.subplots(6, sharex=True)

            figure.suptitle(f'Problem in {scale}')

            axes[0].plot(dtf_spacekernel['year'] - dtf_ref['year'])
            axes[1].plot(dtf_spacekernel['month'] - dtf_ref['month'])
            axes[2].plot(dtf_spacekernel['day'] - dtf_ref['day'])
            axes[3].plot(dtf_spacekernel['hour'] - dtf_ref['hour'])
            axes[4].plot(dtf_spacekernel['minute'] - dtf_ref['minute'])
            axes[5].plot(dtf_spacekernel['second'] - dtf_ref['second'])

            pyplot.show()

            raise error

    # ---------- ---------- ---------- ---------- jd12 -> byear
    def test_byear_from_jd12(self, time_1e3):

        byear_ref = time_1e3.byear
        byear_spacekernel = byear_from_jd12(time_1e3.jd12)

        assert numpy.all(byear_spacekernel == byear_ref)

    # ---------- ---------- ---------- ---------- byear -> jd12
    def test_jd12_from_byear(self, time_1e3):

        jd_ref = time_1e3.jd
        jd12_spacekernel = jd12_from_byear(time_1e3.byear)
        jd_spacekernel = jd_from_jd12(jd12_spacekernel)

        # assert numpy.all(jd_spacekernel == jd_ref)
        assert numpy.allclose(jd_spacekernel, jd_ref)

    # ---------- ---------- ---------- ---------- jd12 -> jyear
    def test_jyear_from_jd12(self, time_1e3):

        jyear_ref = time_1e3.jyear
        jyear_spacekernel = jyear_from_jd12(time_1e3.jd12)

        assert numpy.all(jyear_spacekernel == jyear_ref)

    # ---------- ---------- ---------- ---------- jyear -> jd12
    def test_jd12_from_jyear(self, time_1e3):

        jd_ref = time_1e3.jd
        jd12_spacekernel = jd12_from_jyear(time_1e3.jyear)
        jd_spacekernel = jd_from_jd12(jd12_spacekernel)

        # assert numpy.all(jd_spacekernel == jd_ref)
        assert numpy.allclose(jd_spacekernel, jd_ref)


class TestScaleConversions:

    @pytest.fixture
    def data_1e3(self) -> dict[str, NDArray]:

        time_aspy = TimeTypes.create_data(1000).astropy

        utc = time_aspy.utc
        tt = time_aspy.tt
        tai = time_aspy.tai
        ut1 = time_aspy.ut1

        return {
            'datetime64': utc.datetime64,
            'mjd_utc': utc.mjd,
            'dut': utc.delta_ut1_utc,
            'utc': numpy.hstack([utc.jd1.reshape(-1, 1), utc.jd2.reshape(-1, 1)]),
            'tt': numpy.hstack([tt.jd1.reshape(-1, 1), tt.jd2.reshape(-1, 1)]),
            'tai': numpy.hstack([tai.jd1.reshape(-1, 1), tai.jd2.reshape(-1, 1)]),
            'ut1': numpy.hstack([ut1.jd1.reshape(-1, 1), ut1.jd2.reshape(-1, 1)]),
        }

    def test_tt_from_tai(self, data_1e3) -> None:

        tt_ref = data_1e3['tt']
        tt_spacekernel = tt_from_tai(data_1e3['tai'])

        assert numpy.all(tt_spacekernel.sum(axis=1) == tt_ref.sum(axis=1))

    def test_tai_from_tt(self, data_1e3) -> None:

        tai_ref = data_1e3['tai']
        tai_spacekernel = tai_from_tt(data_1e3['tt'])

        assert numpy.all(tai_spacekernel.sum(axis=1) == tai_ref.sum(axis=1))

    def test_utc_from_tai(self, data_1e3) -> None:

        utc_ref = data_1e3['utc']
        utc_spacekernel = utc_from_tai(data_1e3['tai'])

        assert numpy.all(utc_spacekernel.sum(axis=1) == utc_ref.sum(axis=1))

    def test_tai_from_utc(self, data_1e3) -> None:

        tai_ref = data_1e3['tai']
        tai_spacekernel = tai_from_utc(data_1e3['utc'])

        assert numpy.all(tai_spacekernel.sum(axis=1) == tai_ref.sum(axis=1))

    def test_ut1_from_utc(self, data_1e3) -> None:

        ut1_ref = data_1e3['ut1']
        ut1_spacekernel = ut1_from_utc(data_1e3['utc'])

        try:
            # assert numpy.all(ut1_spacekernel.sum(axis=1) == ut1_ref.sum(axis=1))
            assert numpy.allclose(ut1_spacekernel.sum(axis=1), ut1_ref.sum(axis=1), atol=5e-9, rtol=0.0)

        except AssertionError as error:
            figure, axes = pyplot.subplots(3, sharex=True)

            datetime64_utc = data_1e3['datetime64']

            axes[0].plot(datetime64_utc, ut1_ref.sum(axis=1), label='astropy')
            axes[0].plot(datetime64_utc, ut1_spacekernel.sum(axis=1), label='spacekernel')
            axes[0].legend()

            axes[1].plot(datetime64_utc[1:], numpy.diff(ut1_ref.sum(axis=1)), label='astropy')
            axes[1].plot(datetime64_utc[1:], numpy.diff(ut1_spacekernel.sum(axis=1)), label='spacekernel')
            axes[1].legend()

            axes[2].plot(datetime64_utc, ut1_ref.sum(axis=1) - ut1_spacekernel.sum(axis=1))

            pyplot.show()

            raise error

    def test_utc_from_ut1(self, data_1e3) -> None:

        utc_ref = data_1e3['utc']
        utc_spacekernel = utc_from_ut1(data_1e3['ut1'])

        try:
            # assert numpy.all(utc_spacekernel.sum(axis=1) == utc_ref.sum(axis=1))
            assert numpy.allclose(utc_spacekernel.sum(axis=1), utc_ref.sum(axis=1), rtol=0.0, atol=5e-9)

            # assert False


        except AssertionError as error:
            figure, axes = pyplot.subplots(3, sharex=True)

            datetime64_utc = data_1e3['datetime64']

            axes[0].plot(datetime64_utc, utc_ref.sum(axis=1), label='astropy')
            axes[0].plot(datetime64_utc, utc_spacekernel.sum(axis=1), label='spacekernel')
            axes[0].legend()

            axes[1].plot(datetime64_utc[1:], numpy.diff(utc_ref.sum(axis=1)), label='astropy')
            axes[1].plot(datetime64_utc[1:], numpy.diff(utc_spacekernel.sum(axis=1)), label='spacekernel')
            axes[1].legend()

            axes[2].plot(datetime64_utc, utc_ref.sum(axis=1) - utc_spacekernel.sum(axis=1))

            pyplot.show()

            raise error


class TestTime:

    @pytest.fixture
    def time_1e3(self):
        return TimeTypes.create_data(1000)

    @pytest.fixture
    def time_1e6(self):
        return TimeTypes.create_data(1_000_000)

    # ---------- ---------- ---------- ---------- ---------- instantiate
    def test_instantiate_from_jd12(self, time_1e3):

        jd12 = time_1e3.jd12

        for scale in ['utc', 'tai', 'tt', 'ut1']:

            # ---------- ---------- ---------- ---------- ---------- aspy
            time_aspy = Time_(jd12[:, 0], jd12[:, 1], scale=scale, format='jd')
            jd_aspy = time_aspy.jd

            # ---------- ---------- ---------- ---------- ---------- spacekernel
            time_spacekernel = Time(jd12, scale=scale)
            jd_spacekernel = time_spacekernel.jd

            try:
                assert numpy.all(jd_spacekernel == jd_aspy)

            except AssertionError:

                figure, axes = pyplot.subplots()

                figure.suptitle(f'Problem instantiate from jd12 with {scale}')

                axes.plot(time_1e3.datetime64, jd_aspy, label='astropy')
                axes.plot(time_1e3.datetime64, jd_spacekernel, label='spacekernel')

                pyplot.show()

    def test_instantiate_from_jd(self, time_1e3):

        jd = time_1e3.jd

        for scale in ['utc', 'tai', 'tt', 'ut1']:

            # ---------- ---------- ---------- ---------- ---------- aspy
            time_aspy = Time_(jd, scale=scale, format='jd')
            jd_aspy = time_aspy.jd

            # ---------- ---------- ---------- ---------- ---------- spacekernel
            time_spacekernel = Time(jd, scale=scale, format='jd')
            jd_spacekernel = time_spacekernel.jd

            try:
                assert numpy.all(jd_spacekernel == jd_aspy)

            except AssertionError:

                figure, axes = pyplot.subplots()

                figure.suptitle(f'Problem instantiate from jd with {scale}')

                axes.plot(time_1e3.datetime64, jd_aspy, label='astropy')
                axes.plot(time_1e3.datetime64, jd_spacekernel, label='spacekernel')

                pyplot.show()

    def test_instantiate_from_mjd(self, time_1e3):

        mjd = time_1e3.mjd

        for scale in ['utc', 'tai', 'tt', 'ut1']:

            # ---------- ---------- ---------- ---------- ---------- aspy
            time_aspy = Time_(mjd, scale=scale, format='mjd')
            jd_aspy = time_aspy.jd

            # ---------- ---------- ---------- ---------- ---------- spacekernel
            time_spacekernel = Time(mjd, scale=scale, format='mjd')
            jd_spacekernel = time_spacekernel.jd

            try:
                assert numpy.all(jd_spacekernel == jd_aspy)

            except AssertionError:

                figure, axes = pyplot.subplots()

                figure.suptitle(f'Problem instantiate from mjd with {scale}')

                axes.plot(time_1e3.datetime64, jd_aspy, label='astropy')
                axes.plot(time_1e3.datetime64, jd_spacekernel, label='spacekernel')

                pyplot.show()

    def test_instantiate_from_jyear(self, time_1e3):

        jyear = time_1e3.jyear

        for scale in ['utc', 'tai', 'tt', 'ut1']:

            # ---------- ---------- ---------- ---------- ---------- aspy
            time_aspy = Time_(jyear, scale=scale, format='jyear')
            jd_aspy = time_aspy.jd

            # ---------- ---------- ---------- ---------- ---------- spacekernel
            time_spacekernel = Time(jyear, scale=scale, format='jyear')
            jd_spacekernel = time_spacekernel.jd

            try:
                assert numpy.all(jd_spacekernel == jd_aspy)

            except AssertionError:

                figure, axes = pyplot.subplots()

                figure.suptitle(f'Problem instantiate jyear mjd with {scale}')

                axes.plot(time_1e3.datetime64, jd_aspy, label='astropy')
                axes.plot(time_1e3.datetime64, jd_spacekernel, label='spacekernel')

                pyplot.show()

    def test_instantiate_from_byear(self, time_1e3):

        byear = time_1e3.byear

        for scale in ['utc', 'tai', 'tt', 'ut1']:

            # ---------- ---------- ---------- ---------- ---------- aspy
            time_aspy = Time_(byear, scale=scale, format='jyear')
            jd_aspy = time_aspy.jd

            # ---------- ---------- ---------- ---------- ---------- spacekernel
            time_spacekernel = Time(byear, scale=scale, format='jyear')
            jd_spacekernel = time_spacekernel.jd

            try:
                assert numpy.all(jd_spacekernel == jd_aspy)

            except AssertionError:

                figure, axes = pyplot.subplots()

                figure.suptitle(f'Problem instantiate from byear with {scale}')

                axes.plot(time_1e3.datetime64, jd_aspy, label='astropy')
                axes.plot(time_1e3.datetime64, jd_spacekernel, label='spacekernel')

                pyplot.show()

    def test_instantiate_from_dtf(self, time_1e3):

        dtf = time_1e3.dtf

        for scale in ['utc', 'tai', 'tt', 'ut1']:

            # ---------- ---------- ---------- ---------- ---------- aspy
            time_aspy = Time_(time_1e3.datetime64, scale=scale, format='datetime64')
            jd_aspy = time_aspy.jd

            # ---------- ---------- ---------- ---------- ---------- spacekernel
            time_spacekernel = Time(dtf, scale=scale)
            jd_spacekernel = time_spacekernel.jd

            try:
                assert numpy.all(jd_spacekernel == jd_aspy)

            except AssertionError:

                figure, axes = pyplot.subplots()

                figure.suptitle(f'Problem instantiate from dtf with {scale}')

                axes.plot(time_1e3.datetime64, jd_aspy, label='astropy')
                axes.plot(time_1e3.datetime64, jd_spacekernel, label='spacekernel')

                pyplot.show()

    def test_instantiate_from_datetime64(self, time_1e3):

        datetime64 = time_1e3.datetime64

        for scale in ['utc', 'tai', 'tt', 'ut1']:

            # ---------- ---------- ---------- ---------- ---------- aspy
            time_aspy = Time_(datetime64, scale=scale, format='datetime64', precision=9)
            jd_aspy = time_aspy.jd

            # ---------- ---------- ---------- ---------- ---------- spacekernel
            time_spacekernel = Time(datetime64, scale=scale)
            jd_spacekernel = time_spacekernel.jd

            try:
                assert numpy.all(jd_spacekernel == jd_aspy)

            except AssertionError:

                figure, axes = pyplot.subplots()

                figure.suptitle(f'Problem instantiate from datetime64 with {scale}')

                axes.plot(datetime64, jd_aspy, label='astropy')
                axes.plot(datetime64, jd_spacekernel, label='spacekernel')

                pyplot.show()

    def test_instantiate_from_int64(self, time_1e3):

        int64 = time_1e3.int64

        for scale in ['utc', 'tai', 'tt', 'ut1']:

            # ---------- ---------- ---------- ---------- ---------- aspy
            time_aspy = Time_(time_1e3.datetime64, scale=scale, format='datetime64')
            jd_aspy = time_aspy.jd

            # ---------- ---------- ---------- ---------- ---------- spacekernel
            time_spacekernel = Time(int64, scale=scale)
            jd_spacekernel = time_spacekernel.jd

            try:
                assert numpy.all(jd_spacekernel == jd_aspy)

            except AssertionError:

                figure, axes = pyplot.subplots()

                figure.suptitle(f'Problem instantiate from int64 with {scale}')

                axes.plot(time_1e3.datetime64, jd_aspy, label='astropy')
                axes.plot(time_1e3.datetime64, jd_spacekernel, label='spacekernel')

                pyplot.show()

    def test_instantiate_from_pandas_naive(self, time_1e3):

        datetimeindex = time_1e3.DatetimeIndex
        datetime64 = datetimeindex.to_numpy()

        for scale in ['utc', 'tai', 'tt', 'ut1']:

            # ---------- ---------- ---------- ---------- ---------- aspy
            time_aspy = Time_(datetime64, scale=scale, format='datetime64')
            jd_aspy = time_aspy.jd

            # ---------- ---------- ---------- ---------- ---------- spacekernel
            time_spacekernel = Time(datetimeindex, scale=scale)
            jd_spacekernel = time_spacekernel.jd

            try:
                assert numpy.all(jd_spacekernel == jd_aspy)

            except AssertionError:

                figure, axes = pyplot.subplots()

                figure.suptitle(f'Problem instantiate from naive datetimeindex with {scale}')

                axes.plot(datetime64, jd_aspy, label='astropy')
                axes.plot(datetime64, jd_spacekernel, label='spacekernel')

                pyplot.show()

    def test_instantiate_from_pandas_utc(self, time_1e3):

        datetimeindex_utc = time_1e3.DatetimeIndex_utc

        datetime64 = datetimeindex_utc.tz_localize(None).to_numpy()

        for scale in ['utc', 'tai', 'tt', 'ut1']:

            # ---------- ---------- ---------- ---------- ---------- aspy
            time_aspy = Time_(datetime64, scale='utc', format='datetime64')
            jd_aspy = time_aspy.jd

            # ---------- ---------- ---------- ---------- ---------- spacekernel
            time_spacekernel = Time(datetimeindex_utc, scale=scale)
            jd_spacekernel = time_spacekernel.jd

            try:
                # assert numpy.all(jd_spacekernel == jd_aspy)
                assert numpy.allclose(jd_spacekernel, jd_aspy, rtol=0, atol=5e-10)

            except AssertionError:

                figure, axes = pyplot.subplots(2)

                figure.suptitle(f'Problem instantiate from utc datetimeindex with {scale}')

                axes[0].plot(datetime64, jd_aspy, label='astropy')
                axes[0].plot(datetime64, jd_spacekernel, label='spacekernel')
                axes[0].legend()

                axes[1].plot(datetime64, jd_spacekernel-jd_aspy)

                pyplot.show()

    def test_instantiate_from_pandas_non_utc(self, time_1e3):

        datetimeindex_non_utc = time_1e3.DatetimeIndex_non_utc

        datetime64 = datetimeindex_non_utc.tz_convert('utc').tz_localize(None).to_numpy()

        for scale in ['utc', 'tai', 'tt', 'ut1']:

            # ---------- ---------- ---------- ---------- ---------- aspy
            time_aspy = Time_(datetime64, scale='utc', format='datetime64')
            jd_aspy = time_aspy.jd

            # ---------- ---------- ---------- ---------- ---------- spacekernel
            time_spacekernel = Time(datetimeindex_non_utc, scale=scale)
            jd_spacekernel = time_spacekernel.jd

            try:
                # assert numpy.all(jd_spacekernel == jd_aspy)
                assert numpy.allclose(jd_spacekernel, jd_aspy, rtol=0, atol=5e-10)

            except AssertionError:

                figure, axes = pyplot.subplots(2)

                figure.suptitle(f'Problem instantiate from non-naive datetimeindex with {scale}')

                axes[0].plot(datetime64, jd_aspy, label='astropy')
                axes[0].plot(datetime64, jd_spacekernel, label='spacekernel')
                axes[0].legend()

                axes[1].plot(datetime64, jd_spacekernel-jd_aspy)

                pyplot.show()

    def test_instantiate_from_astropy(self, time_1e3):

        datetime64 = time_1e3.datetime64

        for scale in ['utc', 'tai', 'tt', 'ut1']:

            # ---------- ---------- ---------- ---------- ---------- aspy
            time_aspy = Time_(datetime64, scale=scale, format='datetime64', precision=9)
            jd_aspy = time_aspy.jd

            # ---------- ---------- ---------- ---------- ---------- spacekernel
            time_spacekernel = Time(time_aspy)
            jd_spacekernel = time_spacekernel.jd

            try:
                assert numpy.all(jd_spacekernel == jd_aspy)

            except AssertionError:

                figure, axes = pyplot.subplots()

                figure.suptitle(f'Problem instantiate from astropy with {scale}')

                axes.plot(datetime64, jd_aspy, label='astropy')
                axes.plot(datetime64, jd_spacekernel, label='spacekernel')

                pyplot.show()

    def test_instantiate_from_spacekernel(self, time_1e3):

        datetime64 = time_1e3.datetime64

        for scale in ['utc', 'tai', 'tt', 'ut1']:

            # ---------- ---------- ---------- ---------- ---------- aspy
            time_spacekernel_original = Time(datetime64, scale=scale)
            jd_spacekernel_original = time_spacekernel_original.jd

            # ---------- ---------- ---------- ---------- ---------- spacekernel
            time_spacekernel = Time(time_spacekernel_original)
            jd_spacekernel = time_spacekernel.jd

            try:
                assert numpy.all(jd_spacekernel == jd_spacekernel_original)

            except AssertionError:

                figure, axes = pyplot.subplots()

                figure.suptitle(f'Problem instantiate from spacekernel with {scale}')

                axes.plot(datetime64, jd_spacekernel_original, label='spacekernel original')
                axes.plot(datetime64, jd_spacekernel, label='spacekernel')

                pyplot.show()

    def test_instantiate_from_str(self, time_1e3):

        datetimeiso = time_1e3.str

        aspy_time = Time_(datetimeiso)
        spacekernel_time = Time(datetimeiso)

        assert numpy.all(Time(aspy_time) == spacekernel_time)

        Time(datetimeiso[0])  # just to make sure it won't crash

    # ---------- ---------- ---------- ---------- ---------- scale conversion
    def test_scale_transform(self, time_1e3):

        datetime64 = time_1e3.datetime64

        # ---------- ---------- ---------- ---------- ---------- from utc
        aspy_utc_time = Time_(datetime64, scale='utc', format='datetime64', precision=9)
        spacekernel_utc_time = Time(datetime64, scale='utc')

        assert numpy.all(aspy_utc_time.utc.jd == spacekernel_utc_time.utc.jd)
        assert numpy.all(aspy_utc_time.tai.jd == spacekernel_utc_time.tai.jd)
        assert numpy.all(aspy_utc_time.tt.jd == spacekernel_utc_time.tt.jd)
        assert numpy.allclose(aspy_utc_time.ut1.jd, spacekernel_utc_time.ut1.jd, rtol=0, atol=5e-9)

        # ---------- ---------- ---------- ---------- ---------- from tai
        aspy_tai_time = Time_(datetime64, scale='tai', format='datetime64', precision=9)
        spacekernel_tai_time = Time(datetime64, scale='tai')

        assert numpy.all(aspy_tai_time.utc.jd == spacekernel_tai_time.utc.jd)
        assert numpy.all(aspy_tai_time.tai.jd == spacekernel_tai_time.tai.jd)
        assert numpy.all(aspy_tai_time.tt.jd == spacekernel_tai_time.tt.jd)
        assert numpy.allclose(aspy_tai_time.ut1.jd, spacekernel_tai_time.ut1.jd, rtol=0, atol=5e-9)

        # ---------- ---------- ---------- ---------- ---------- from tt
        aspy_tt_time = Time_(datetime64, scale='tt', format='datetime64', precision=9)
        spacekernel_tt_time = Time(datetime64, scale='tt')

        assert numpy.all(aspy_tt_time.utc.jd == spacekernel_tt_time.utc.jd)
        assert numpy.all(aspy_tt_time.tai.jd == spacekernel_tt_time.tai.jd)
        assert numpy.all(aspy_tt_time.tt.jd == spacekernel_tt_time.tt.jd)
        assert numpy.allclose(aspy_tt_time.ut1.jd, spacekernel_tt_time.ut1.jd, rtol=0, atol=5e-9)

        # ---------- ---------- ---------- ---------- ---------- from ut1
        aspy_ut1_time = Time_(datetime64, scale='ut1', format='datetime64', precision=9)
        spacekernel_ut1_time = Time(datetime64, scale='ut1')

        assert numpy.allclose(aspy_ut1_time.utc.jd, spacekernel_ut1_time.utc.jd, rtol=0, atol=5e-9)
        assert numpy.allclose(aspy_ut1_time.tai.jd, spacekernel_ut1_time.tai.jd, rtol=0, atol=5e-9)
        assert numpy.allclose(aspy_ut1_time.tt.jd, spacekernel_ut1_time.tt.jd, rtol=0, atol=5e-9)
        assert numpy.all(aspy_ut1_time.ut1.jd == spacekernel_ut1_time.ut1.jd)

    def test_range(self):

        t = Time.range(start='2021-03-18', end='2022-10-18', step=3600)

        print()
        print(t)

    def test_rich_comparison(self) -> None:
        print()

        t = Time.range(start='2021-03-18', end='2022-10-18', step=3600)
        t_pandas = pandas.date_range(start='2021-03-18', end='2022-10-18', freq='3600s')
        t_numpy = t_pandas.to_numpy()

        assert numpy.all(t == t_pandas)
        assert numpy.all(t == t_numpy)

        assert numpy.all((t > '2022') == (t_pandas > '2022'))
        assert numpy.all((t >= '2022') == (t_pandas >= '2022'))
        assert numpy.all((t < '2022') == (t_pandas < '2022'))
        assert numpy.all((t <= '2022') == (t_pandas <= '2022'))

    def test_get_item(self):
        print()

        t = Time.range(start='2021-03-18', end='2022-10-18', step=3600)
        t_pandas = pandas.date_range(start='2021-03-18', end='2022-10-18', freq='3600s')
        t_numpy = t_pandas.to_numpy()

        # test slice
        assert numpy.all(t[3:10] == Time(t_numpy[3:10]))
        assert numpy.all(t[3:10:3] == Time(t_numpy[3:10:3]))
        assert numpy.all(t[100:-100] == Time(t_numpy[100:-100]))

        assert numpy.all(t['2022':] == Time(t_pandas[t_pandas >= '2022']))
        assert numpy.all(t['2021-08':'2022-03'] == Time(t_pandas[(t_pandas >= '2021-08') & (t_pandas <'2022-03')]))

        # test ndarray of bools
        assert numpy.all(t[t_pandas > '2021-08'] == Time(t_pandas[t_pandas > '2021-08']))
        assert numpy.all(t[(t_pandas > '2021-08').tolist()] == Time(t_pandas[t_pandas > '2021-08']))

        # test arrays of integers
        indices = [0, 10, 20]
        assert numpy.all(t[indices] == Time(t_numpy[indices]))

        print(t[[0, 10, 20]])

        print(t[-5])

        indices = numpy.array(indices)
        assert numpy.all(t[indices] == Time(t_numpy[indices]))

        for index in indices:
            assert t[index] == Time(t_numpy[index])

        # test indices
        assert t[100] == Time(t_numpy[100])

    def test_math_operations(self):
        print()

        t = Time.range(start='2021-03-18', end='2022-10-18', step=3600)
        t_pandas = pandas.date_range(start='2021-03-18', end='2022-10-18', freq='3600s')

        assert numpy.all(t + 30 == Time(t_pandas + pandas.Timedelta(30, unit='s')))
        assert numpy.all(t + '30d' == Time(t_pandas + pandas.Timedelta(30, unit='d')))
        assert numpy.all(t - 30 == Time(t_pandas - pandas.Timedelta(30, unit='s')))
        assert numpy.all(t - '30d' == Time(t_pandas - pandas.Timedelta(30, unit='d')))

        assert numpy.all(t[1:] - t[:-1] == 3600)

        print(t - t[0])

    def test_iterator(self):
        print()

        time = Time.range(start='2021-03-18', end='2022-10-18', step=3600*24)

        for t in time:
            print(t + 30)

    # ---------- ---------- ---------- ---------- ---------- performance
    @profile
    def test_time_instantiate_performance(self):

        datetime64 = TimeTypes.create_data(1_000_000).datetime64

        Time_(datetime64, format='datetime64')
        Time(datetime64)
