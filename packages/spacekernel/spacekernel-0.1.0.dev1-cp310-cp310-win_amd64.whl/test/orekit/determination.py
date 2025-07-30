#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

import numpy

import pandas

from pathlib import Path

from gs25.orekit import Orekit

# ---------- ---------- ---------- ---------- ---------- ty
from typing import TextIO


class GroundSensor:

    def __init__(self, **kwargs) -> None:
        ...

    # ========== ========== ========== ========== ========== class attributes
    ...

    # ========== ========== ========== ========== ========== special methods
    ...

    # ========== ========== ========== ========== ========== private methods
    ...

    # ========== ========== ========== ========== ========== protected methods
    ...

    # ========== ========== ========== ========== ========== public methods
    ...

    # ---------- ---------- ---------- ---------- ---------- properties
    @property
    def id(self) -> int | None:
        try:
            return self._id
        except AttributeError:
            self._id = None
            return self._id

    @property
    def operator(self) -> str | None:
        try:
            return self._operator
        except AttributeError:
            self._operator = None
            return self._operator



# ========== ========== ========== ========== ========== ==========
class TDM:
    """
    This class reads a TDM file and parses it.

    only ANGLE_1, ANGLE_2 and RANGE keywords are currently supported.

    References:
        - CCSDS standard: Tracking Data Messages (https://ccsds.org/wp-content/uploads/gravity_forms/5-448e85c647331d9cbaf66c096458bdd5/2025/01//503x0b2c1_tc2136.pdf
        - TDM header section: Table 3-2
        - TDM metadata section: Table 3-3
        - TDM data section: Section 3.4 and Table 3-5
    """
    # ========== ========== ========== ========== ========== class attributes
    header_keys = [
        'CCSDS_TDM_VERS',
        # 'COMMENT'
        'CREATION_DATE',
        'ORIGINATOR',
        'MESSAGE_ID'
    ]

    metadata_keys = [
        # 'COMMENT',
        'TRACK_ID',
        'DATA_TYPES',
        'TIME_SYSTEM',
        'START_TIME',
        'STOP_TIME',
        'PARTICIPANT',
        'MODE',
        'PATH',
        'EPHEMERIS_NAME',
        'TRANSMIT_BAND',
        'RECEIVE_BAND',
        'TURNAROUND_NUMERATOR',
        'TURNAROUND_DENOMINATOR',
        'TIMETAG_REF',
        'INTEGRATION_INTERVAL',
        'INTEGRATION_REF',
        'FREQ_OFFSET',
        'RANGE_MODE',
        'RANGE_MODULUS',
        'RANGE_UNITS',
        'ANGLE_TYPE',
        'REFERENCE_FRAME',
        'INTERPOLATION',
        'INTERPOLATION_DEGREE',
        'DOPPLER_COUNT_BIAS',
        'DOPPLER_COUNT_SCALE',
        'DOPPLER_COUNT_ROLLOVER',
        'TRANSMIT_DELAY',
        'RECEIVE_DELAY',
        'DATA_QUALITY',
        'CORRECTION_',
        'CORRECTIONS_APPLIED'
    ]

    data_keys = [
        'ANGLE_1',
        'ANGLE_2',
        'RANGE',
    ]

    # ========== ========== ========== ========== ========== special methods
    def __init__(self, filepath: Path|str) -> None:
        self._filepath = Path(filepath)

        self.__read_tdm()


    # ========== ========== ========== ========== ========== private methods
    def __read_tdm(self) -> pandas.DataFrame:

        header = {}
        metadata = {}
        data = []

        with self.filepath.open() as file:

            section = 'header'

            for line in file:

                # ========== ========== ========== ignore empty lines
                if line == '\n':
                    continue

                # ========== ========== ========== define section
                if line.startswith('META_START'):
                    section = 'metadata'
                    continue

                if line.startswith('META_STOP'):
                    section = None
                    continue

                if line.startswith('DATA_START'):
                    section = 'data'
                    continue

                if line.startswith('DATA_STOP'):
                    section = None
                    break

                # ========== ========== ==========
                match section:

                    case 'header':

                        if line.startswith('COMMENT'):
                            header['COMMENT'] = line.replace('COMMENT', '').strip()

                        else:
                            key, value = [part.strip() for part in line.split('=')]
                            header[key] = value

                    case 'metadata':
                        if line.startswith('COMMENT'):
                            metadata['COMMENT'] = line.replace('COMMENT', '').strip()

                        else:
                            key, value = [part.strip() for part in line.split('=')]
                            metadata[key] = value

                    case 'data':
                        keyword, value = [part.strip() for part in line.split('=')]
                        time, measurement = value.split()

                        data.append({
                            'time': time[:-1] if time.endswith('Z') else time,
                            'keyword': keyword,
                            'measurement': measurement,
                        })

                    case None:
                        continue

        # ========== ========== ========== creating data frame
        data = pandas.DataFrame(data)

        # ---------- ---------- ---------- parse measurement time
        try:
            data['time'] = pandas.to_datetime(data['time'], format='%Y-%jT%H:%M:%S.%f')
        except Exception:
            data['time'] = pandas.to_datetime(data['time'])

        data.sort_values('time', inplace=True)
        data.index += 1

        # ---------- ---------- ---------- parse measurement values
        assert all(keyword in self.data_keys for keyword in data.keyword.unique()), f"Only {self.data_keys} keywords are currently supported."

        data['measurement'] = data['measurement'].astype(float)

        # ---------- ---------- angles
        select_angles = data.keyword.str.startswith('ANGLE')
        data.loc[select_angles, 'measurement'] = numpy.deg2rad(data['measurement'][select_angles])

        # ---------- ---------- range
        select_range = data.keyword == 'RANGE'

        if 'RANGE_UNITS' not in metadata or metadata['RANGE_UNITS'].lower() == 'km':
            data.loc[select_range, 'measurement'] *= 1000

        elif metadata['RANGE_UNITS'].lower() == 's':
            data.loc[select_range, 'measurement'] *= 299_792_458

        else:
            raise NotImplementedError(f"Cannot parse range units '{metadata['RANGE_UNITS']}'")

        # ========== ========== ========== ========== ========== ==========
        self._header = pandas.Series(header)
        self._metadata = pandas.Series(metadata)
        self._data = data

    # ========== ========== ========== ========== ========== protected methods
    ...

    # ========== ========== ========== ========== ========== public methods
    ...

    # ---------- ---------- ---------- ---------- ---------- properties
    @property
    def filepath(self) -> Path:
        return self._filepath

    @property
    def header(self) -> pandas.Series:
        return self._header

    @property
    def metadata(self) -> pandas.Series:
        return self._metadata

    @property
    def data(self) -> pandas.DataFrame:
        """Measurement data (in SI)"""
        return self._data


# ========== ========== ========== ========== ========== ==========


class OrbitDetermination:

    def __init__(self, *tdm, initial_state):
        self.tdm = tdm
        self.initial_state = initial_state


# ========== ========== ========== ========== ========== ========== load TDM
def _load_tdm(tdm_filepath: Path|str) -> 'org.orekit.files.ccsds.ndm.tdm.Tdm':

    from org.orekit.files.ccsds.ndm.tdm import TdmParser, IdentityConverter
    from org.orekit.data import DataSource
    from org.orekit.utils import IERSConventions
    from org.orekit.data import DataContext
    from org.orekit.files.ccsds.ndm import ParsedUnitsBehavior

    from java.io import File as JFile, FileInputStream

    # 1. Get the default data context
    data_context = DataContext.getDefault()

    # 2. Create the parser with required parameters
    parser = TdmParser(
        IERSConventions.IERS_2010,  # Earth orientation model
        True,  # Simple EOP (True) or full history (False)
        data_context,  # Data context for frames/time
        ParsedUnitsBehavior.STRICT_COMPLIANCE, # ParsedUnitsBehavior (None for default)
        IdentityConverter(),
        []
    )

    # parser = TdmParser(IERSConventions.IERS_2010, True, data_context, None, None, None)

    # 3. Now parse your TDM file
    file = JFile(str(tdm_filepath))
    ds = DataSource(file)
    tdm = parser.parseMessage(ds)

    return tdm


def load_tdm(tdm_filepath: Path|str) -> list:
    with Orekit():
        return _load_tdm(tdm_filepath)

# ========== ========== ========== ========== ========== ==========
def _get_measurements(tdm: 'org.orekit.files.ccsds.ndm.tdm.Tdm') -> list:

    from org.orekit.estimation.measurements import Range, RangeRate, AngularAzEl, ObservableSatellite
    from org.orekit.time import AbsoluteDate

    sat = ObservableSatellite(0)

    for segment in tdm.getSegments():

        # Access the observation data
        for obs in segment.getData().getObservations():
            # 2.1) Identify measurement type
            obs_type = obs.getType()
            obs_epoch = obs.getEpoch()

            # print(obs_type, obs_epoch, obs.getMeasurement())
            print(obs_type)



# ========== ========== ========== ========== ========== ==========
def determine_orbit(*tdm_filepath, **kwargs):

    with Orekit():

        for tdm in [_load_tdm(_tdm_filepath) for _tdm_filepath in tdm_filepath]:
            _get_measurements(tdm)

