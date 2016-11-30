# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
import shutil
import scrapy
from scrapy.utils.request import request_fingerprint
import requests

sys.path.insert(0, '/home/erliang/Dev/Project/hfut')

from hfut import ENV
from hfut.session import StudentSession
from hfut.interface import GetCode, GetTeachingPlan, SearchCourse, GetClassInfo, GetClassStudents
from hfut.util import sort_hosts

from ..items import MajorItem, TermItem, CourseItem, TeachingPlanItem, TeachingClassItem, StudentItem

ENV['SOUP_FEATURES'] = ['lxml']


class MockResponse(requests.Response):
    content = b''

    def __init__(self, scrapy_response):
        super(MockResponse, self).__init__()
        # requests.adapters.HTTPAdapter#build_response
        self.url = scrapy_response.url
        self.status_code = scrapy_response.status
        self.content = scrapy_response.body


class HfutSystemSpider(scrapy.Spider):
    name = 'hfut_system_spider'

    def __init__(self, account, password, campus, *args, **kwargs):
        super(HfutSystemSpider, self).__init__(*args, **kwargs)
        self.session = StudentSession(account, password, campus)
        host_rank = sort_hosts()
        self.logger.info('选择最快的服务器: %s', host_rank)
        self.session.host = host_rank[0][1]
        self.session.login()

        self.no_results_request_records_dir = 'no_results_requests'
        if os.path.exists(self.no_results_request_records_dir):
            shutil.rmtree(self.no_results_request_records_dir)

    def request_transform(self, interface, callback=None, meta=None, priority=0, dont_filter=False, errbcak=None):
        prep = self.session.prepare_request(interface.make_request())
        return scrapy.Request(
            url=prep.url,
            callback=callback,
            method=prep.method,
            # requests.models.PreparedRequest#prepare_headers 类型为 <class 'requests.structures.CaseInsensitiveDict'>
            # scrapy.utils.datatypes.CaselessDict#update 判断时 isinstance(seq, dict) 会出错
            headers=dict(prep.headers),
            body=prep.body,
            # 'PreparedRequest' object has no attribute 'cookies', 因为 PreparedRequest 已经将 cookies 存到了 headers
            # requests.models.PreparedRequest#prepare_cookies
            cookies=prep._cookies.get_dict(),
            meta=meta,
            encoding=ENV['SITE_ENCODING'],
            priority=priority,
            dont_filter=dont_filter,
            errback=errbcak
        )

    def record_no_results_request(self, request):
        key = request_fingerprint(request)
        # 同时使用一个文件会产生写竞争
        with open(os.path.join(self.no_results_request_records_file, key), 'wb') as fp:
            fp.write(key)

    def start_requests(self):
        # http://scrapy.readthedocs.io/en/latest/topics/request-response.html#scrapy.http.Request
        interface = GetCode()
        yield self.request_transform(interface, meta={'interface': interface}, dont_filter=True)

    def parse(self, response):
        prev_interface = response.meta['interface']
        # @structure {'专业': [{'专业代码': str, '专业名称': str}], '学期': [{'学期代码': str, '学期名称': str}]}
        code = prev_interface.parse(MockResponse(response))
        if not code:
            self.record_no_results_request(response.request)
        # todo: using for profile
        code = {
            '专业': [
                {'专业代码': '0120123111', '专业名称': '2012*机械设计制造及其自动化'}
            ],
            '学期': [
                {'学期代码': '021', '学期名称': '2012-2013学年第一学期'}
            ]
        }
        terms = code['学期']
        majors = code['专业']
        term_items = {}
        for term in terms:
            term_item = TermItem(code=term['学期代码'], name=term['学期名称'])
            term_items[term['学期代码']] = term_item
            yield term_item

            interface = GetTeachingPlan(term_item['code'], kclx='x')
            yield self.request_transform(
                interface,
                callback=self.parse_course,
                meta={
                    'interface': interface,
                    'term_item': term_item,
                    'major_item': None
                }
            )

        max_term_number = int(terms[-1]['学期代码'])
        self.logger.info('当前最大学期为 %s', max_term_number)
        for major in majors:
            major_item = MajorItem(code=major['专业代码'], name=major['专业名称'])
            yield major_item

            start_year = int(major_item['name'][:4])
            start = (start_year - 2001) * 2 - 1
            end = start + 7
            if max_term_number < end:
                end = max_term_number
                for i in range(start, end + 1):
                    term_code = '%03d' % i
                    term_item = term_items[term_code]

                    interface = GetTeachingPlan(term_item['code'], zydm=major_item['code'])
                    yield self.request_transform(
                        interface,
                        callback=self.parse_course,
                        meta={
                            'interface': interface,
                            'term_item': term_item,
                            'major_item': major_item
                        }
                    )

    teaching_class_synced_flags = set()

    def parse_course(self, response):
        prev_interface = response.meta['interface']
        term_item = response.meta['term_item']
        major_item = response.meta['major_item']

        courses = prev_interface.parse(MockResponse(response))
        if not courses:
            self.record_no_results_request(response.request)
        for course in courses:
            course_item = CourseItem(
                code=course['课程代码'],
                name=course['课程名称'],
                credit=course['学分'],
                hours=course['学时'],
                belong_to=course['开课单位']
            )
            yield course_item
            # 简化了代码但增加了判断次数
            if major_item:
                teaching_plan_item = TeachingPlanItem(
                    term_code=term_item['code'],
                    course_code=course_item['code'],
                    major_code=major_item['code']
                )
                yield teaching_plan_item

            # 不同的专业有相同的计划
            key = term_item['code'] + course_item['code']
            # This method, as well as any other Request callback,
            # must return an iterable of Request and/or dicts or Item objects.
            if key not in self.teaching_class_synced_flags:
                interface = SearchCourse(xqdm=term_item['code'], kcdm=course_item['code'])
                yield self.request_transform(
                    interface,
                    callback=self.parse_teaching_class_base,
                    meta={
                        'interface': interface,
                        'term_item': term_item,
                        'major_item': major_item,  # 一直往下传递用于最后学生专业的判断
                        'course_item': course_item
                    }
                )

    def parse_teaching_class_base(self, response):
        prev_interface = response.meta['interface']
        term_item = response.meta['term_item']
        major_item = response.meta['major_item']
        course_item = response.meta['course_item']

        key = term_item['code'] + course_item['code']
        self.teaching_class_synced_flags.add(key)

        # @structure [{'任课教师': str, '课程名称': str, '教学班号': str, 'c': str, '班级容量': int}]
        teaching_classes = prev_interface.parse(MockResponse(response))
        if not teaching_classes:
            self.record_no_results_request(response.request)
        for base_class_info in teaching_classes:
            interface = GetClassInfo(xqdm=term_item['code'], kcdm=course_item['code'], jxbh=base_class_info['教学班号'])
            yield self.request_transform(
                interface,
                callback=self.parse_teaching_class,
                meta={
                    'interface': interface,
                    'term_item': term_item,
                    'major_item': major_item,
                    'course_item': course_item,
                    'base_class_info': base_class_info,
                }
            )

    def parse_teaching_class(self, response):
        prev_interface = response.meta['interface']
        term_item = response.meta['term_item']
        major_item = response.meta['major_item']
        course_item = response.meta['course_item']
        base_class_info = response.meta['base_class_info']

        # @structure {'校区': str,'开课单位': str,'考核类型': str,'课程类型': str,'课程名称': str,'教学班号': str,
        # '起止周': str, '时间地点': str,'学分': float,'性别限制': str,'优选范围': str,'禁选范围': str,'选中人数': int,'备 注': str}
        class_info = prev_interface.parse(MockResponse(response))
        if not class_info:
            self.record_no_results_request(response.request)
        teaching_class_item = TeachingClassItem(
            term_code=term_item['code'],
            course_code=course_item['code'],

            number=base_class_info['教学班号'],
            size=base_class_info['班级容量'],

            selected=class_info['选中人数'],
            course_type=class_info['课程类型'],
            exam_type=class_info['考核类型'],
            campus=class_info['校区'],
            weeks=class_info['起止周'],
            time_and_place=class_info['时间地点'],
            sex_limit=class_info['性别限制'],
            preferred_scope=class_info['优选范围'],
            forbidden_scope=class_info['禁选范围'],
            remark=class_info['备注']
        )
        # 还要添加学生的关系
        # yield teaching_class_item

        interface = GetClassStudents(xqdm=term_item['code'], kcdm=course_item['code'], jxbh=base_class_info['教学班号'])
        yield self.request_transform(
            interface,
            callback=self.parse_student,
            meta={
                'interface': interface,
                'major_item': major_item,
                'teaching_class_item': teaching_class_item
            },
            errbcak=lambda response: self.record_no_results_request(response.request)
        )

    def parse_student(self, response):
        # fixme: 部分请求没有匹配到信息, 页面乱码
        prev_interface = response.meta['interface']
        # todo: 待用来判断学生专业
        # major_item = response.meta['major_item']
        teaching_class_item = response.meta['teaching_class_item']
        teaching_class_item['student_codes'] = []
        # 每个教学班级有很多学生, 有正常的, 重修的
        # 学号年份与最近一个学期专业课程中对应专业年份相等的学生即为该专业
        students = prev_interface.parse(MockResponse(response))
        students = students.get('学生', [])

        for student in students:
            student_item = StudentItem(
                code=student['学号'],
                name=student['姓名'].rstrip('*'),
                sex='女' if student['姓名'].endswith('*') else '男'
            )
            yield student_item
            teaching_class_item['student_codes'].append(student_item['code'])
        yield teaching_class_item
