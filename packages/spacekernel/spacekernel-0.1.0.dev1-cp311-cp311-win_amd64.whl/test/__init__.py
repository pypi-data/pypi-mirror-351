#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

from line_profiler import LineProfiler

from typing import Callable


def profile(func: Callable) -> Callable:

    def _func(*args, **kwargs):
        profiler = LineProfiler()
        profiler.add_function(func)
        profiler.enable_by_count()
        result = func(*args, **kwargs)
        profiler.disable_by_count()

        with open(f'profile_{func.__name__}.txt', 'w') as file:
            profiler.print_stats(stream=file)

        return result

    return _func
