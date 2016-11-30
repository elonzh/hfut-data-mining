# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import logging

import hfut


def init_logger():
    lg = logging.Logger('hfut', level=logging.INFO)
    # https://docs.python.org/3/library/logging.html#logrecord-attributes
    fmt = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    lg.addHandler(sh)
    fh = logging.FileHandler('sync.log', mode='w')
    fh.setFormatter(fmt)
    fh.setLevel(logging.WARNING)
    lg.addHandler(fh)
    return lg


def set_hfut_log():
    h = logging.FileHandler('hfut.log', mode='w')
    h.setLevel(logging.WARNING)
    hfut.logger.addHandler(h)


logger = init_logger()
set_hfut_log()
