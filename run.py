# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import logging

import pymongo
from hfut import Student

from spider import DatabaseManager, JobManager, Spider, logger, init_db
from spider.db import report_db

if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    shortcut = Student(2013217413, '123456789012', 'XC')
    c = pymongo.MongoClient()

    db = c['hfut']
    init_db(db)

    # 初始化任务池
    # 合适的数据库任务池大小和缓冲区大小能更好的利用带宽
    # 数据库记录的最大并发为 db_pool_size * batch_size
    # 当请求池大小大于20时很容易导致服务器错误抓取不到结果
    job_manager = JobManager(pool_size=20)
    db_manager = DatabaseManager(db, batch_size=80)

    j = Spider(shortcut, job_manager, db_manager)

    j.crawl()

    # def patch():
    #     for i in range(21, 31):
    #         term = '%03d' % i
    #         yield term, None, '_'
    #         # for args in j.iter_teaching_class(term, course_name='_'):
    #         #     yield args
    #
    #
    # jobs = (patch, j.iter_teaching_class, j.sync_students)
    # job_manager.jobs = jobs
    #
    # logger.info('Crawl start!'.center(72, '='))
    # job_manager.start()
    # logger.info('Jobs are all dispatched. Waiting for database requests handling.')
    # db_manager.join()
    # logger.info('Crawl finished!'.center(72, '='))
    # report_db(db_manager.db)
