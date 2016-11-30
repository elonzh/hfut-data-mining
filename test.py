# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from unittest import TestCase, main

import hfut
import six

if six.PY3:
    from unittest import mock
else:
    import mock

import pymongo

from spider.job import JobDispatcher
from spider.util import profile


class Test(TestCase):
    def setUp(self):
        client = pymongo.MongoClient()
        client.drop_database('test')
        db = client['test']
        self.term_code = '021'
        self.major_code = '0120123111'
        self.p = mock.patch(
            'spider.job.JobDispatcher.iter_term_and_major',
            lambda v: ((self.term_code, None), (self.term_code, self.major_code))
        )
        self.p.start()
        self.shortcut = hfut.Student(2013217413, '123456789012', 'XC')
        self.j = JobDispatcher(self.shortcut, db=db)

    def tearDown(self):
        self.p.stop()

    @profile
    def test_dfs_stability(self):
        # self.j.crawl()
        self.j.crawl('bfs')
        self.check()

    def check(self):
        # 专业和学期被 patch 掉了
        self.assertEqual(self.j.db['major'].count(), 0)
        self.assertEqual(self.j.db['term'].count(), 0)

        self.assertEqual(self.j.db['course'].count(), 9)
        self.assertEqual(self.j.db['plan'].count(), 9)
        self.assertEqual(self.j.db['class'].count(), 201)
        self.assertEqual(self.j.db['student'].count(), 2621)
        self.assertEqual(self.j.db['class_student'].count(), 20236)
        # plan_b = self.shortcut.get_teaching_plan(self.term_code, zydm=self.major_code)
        # self.assertEqual(self.j.db['plan'].count(), len(plan_b))
        #
        # plan_x = self.shortcut.get_teaching_plan(self.term_code, kclx='x')
        # plan_x.extend(plan_b)
        # self.assertEqual(self.j.db['course'].count(), len(plan_x))
        #
        # class_count = 0
        # class_student_count = 0
        # student_codes = set()
        # for p in plan_x:
        #     classes = self.shortcut.search_course(xqdm=self.term_code, kcdm=p['课程代码'])
        #     class_count += len(classes)
        #     for c in classes:
        #         students = self.shortcut.get_class_students(xqdm=self.term_code, kcdm=p['课程代码'], jxbh=c['教学班号'])['学生']
        #         class_student_count += len(students)
        #         student_codes.update(map(lambda v: v['学号'], students))
        # self.assertEqual(self.j.db['class'].count(), class_count)
        # self.assertEqual(self.j.db['class_student'].count(), class_student_count)
        # self.assertEqual(self.j.db['student'].count(), len(student_codes))



if __name__ == '__main__':
    main(argv=[__file__, 'Test.test_dfs_stability'])
    # main(argv=[__file__, 'Test.test_bfs_stability'])
