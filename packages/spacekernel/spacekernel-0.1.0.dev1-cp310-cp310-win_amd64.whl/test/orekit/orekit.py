#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

from __future__ import annotations

import jpype
import jpype.imports

from pathlib import Path

from typing import Any



here = Path(__file__).parent


class Orekit:

    orekit_jar = here / 'orekit-13.0.jar'
    data_dir = here / 'data'

    def __enter__(self) -> Orekit:

        hipparchus = [str(jar) for jar in (here / 'hipparchus-4.0.1-bin').glob('*.jar')]

        jpype.startJVM(
            classpath=[str(self.orekit_jar)] + hipparchus,
            convertStrings=True
        )


        from java.io import File as JFile
        from org.orekit.data import DataContext, DirectoryCrawler


        crawler = DirectoryCrawler(JFile(str(self.data_dir)))
        manager = DataContext.getDefault().getDataProvidersManager()
        manager.addProvider(crawler)

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        jpype.shutdownJVM()


if __name__ == '__main__':

    with Orekit():

        from org.orekit.time import AbsoluteDate, TimeScalesFactory

        # Test
        utc = TimeScalesFactory.getUTC()
        date = AbsoluteDate(2024, 6, 1, 12, 0, 0.0, utc)
        print(f"Current UTC time: {date}")