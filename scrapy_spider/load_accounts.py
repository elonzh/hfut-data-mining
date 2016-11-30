# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import logging
import csv
from multiprocessing.dummy import Pool

from hfut import Student, SystemLoginFailed

from hfut_system.db import StudentTable


class DataLoader:
    success_count = 0
    error_count = 0
    logger = logging.Logger('data-loader', logging.INFO)

    def __init__(self):
        self.pool = Pool(5)

    def load_student(self, row):
        number, name, account, password = row
        student = Student(account=account, password=password, campus='XC')
        try:
            student.session.login()
        except SystemLoginFailed:
            self.error_count += 1
            self.logger.warning('登录失败: [%s]%s', name, account)
        else:
            self.success_count += 1
            self.logger.info('导入成功: [%s]%s', name, account)

    def load(self):
        with open('/home/erliang/Dev/Project/hfut-spes/data/2016/students.csv') as fp:
            self.pool.map_async(self.load_student, csv.reader(fp))
