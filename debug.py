# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import logging

import pymongo
from gevent.pool import Pool
from gevent.monkey import patch_all

import hfut
from spider.db import report_db

patch_all()
# 使用 lxml 加快解析速度
hfut.ENV['SOUP_FEATURES'] = 'lxml'
# 关闭请求参数检查
hfut.ENV['REQUEST_ARGUMENTS_CHECK'] = False

hfut.logger.setLevel(logging.INFO)
s = hfut.Guest('XC')
p = Pool(10)
ss = []


def func(term):
    rv = s.search_course(xqdm=term, kcmc='_')
    ss.append(len(rv))
    print('%s : %d' % (term, len(rv)))


for i in range(21, 31):
    term = '%03d' % i
    p.spawn(func, term)

p.join()


print(sum(ss))

c = pymongo.MongoClient()

db = c['hfut']

report_db(db)
