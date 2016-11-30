# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import hfut
from gevent.monkey import patch_all

from .db import init_db
from .log import logger
from .manager import DatabaseManager, JobManager
from .spider import Spider

# 使用 lxml 加快解析速度
hfut.ENV['SOUP_FEATURES'] = 'lxml'
# 关闭请求参数检查
hfut.ENV['REQUEST_ARGUMENTS_CHECK'] = False
hfut.ENV['XC_HOSTS'].pop(0)
ranks = hfut.util.sort_hosts(hfut.ENV['XC_HOSTS'], path='teacher/asp/Jskb_table.asp')
logger.info('Using fast server: [%.2fms]%s', *ranks[0])
hfut.ENV['XC'] = ranks[0][1]

# patch thread 会导致测速阻塞, 但是不 patch pymongo 有无法异步, 无奈之举
patch_all()

