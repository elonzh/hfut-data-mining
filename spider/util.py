# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import cProfile
import pstats
import time
from functools import wraps

import hfut

from .log import logger


def term_range(major_name, max_term_number):
    start_year = int(major_name[:4])
    start = (start_year - 2001) * 2 - 1
    end = start + 7
    if max_term_number < end:
        end = max_term_number
    return range(start, end + 1)


def elapse_dec(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        start = time.time()
        rv = func(*args, **kwargs)
        end = time.time()
        elapsed = end - start
        logger.info('Execution cost of %s(args: %s, kwargs: %s): %f sec.', func.__name__, args, kwargs, elapsed)
        return rv

    return wrap


def profile(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        rv = func(*args, **kwargs)
        pr.disable()
        # 文件时间戳间隔 5 min
        with open('%s_%d.txt' % (func.__name__, time.time() // 300), 'w') as f:
            sortby = 'cumulative'
            pstats.Stats(pr, stream=f).strip_dirs().sort_stats(sortby).print_stats()
        return rv

    return wrap
