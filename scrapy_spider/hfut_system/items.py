# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MajorItem(scrapy.Item):
    code = scrapy.Field()
    name = scrapy.Field()


class TermItem(scrapy.Item):
    code = scrapy.Field()
    name = scrapy.Field()


class CourseItem(scrapy.Item):
    code = scrapy.Field()
    name = scrapy.Field()
    credit = scrapy.Field()
    hours = scrapy.Field()
    belong_to = scrapy.Field()


class TeachingPlanItem(scrapy.Item):
    term_code = scrapy.Field()
    course_code = scrapy.Field()
    major_code = scrapy.Field()


class TeachingClassItem(scrapy.Item):
    term_code = scrapy.Field()
    course_code = scrapy.Field()
    student_codes = scrapy.Field()

    # fixme: 放在哪比较合适？
    course_type = scrapy.Field()
    exam_type = scrapy.Field()

    number = scrapy.Field()
    campus = scrapy.Field()
    # weeks = ArrayField(base_field=models.PositiveSmallIntegerField())
    weeks = scrapy.Field()
    time_and_place = scrapy.Field()
    size = scrapy.Field()
    selected = scrapy.Field()

    sex_limit = scrapy.Field()
    preferred_scope = scrapy.Field()
    forbidden_scope = scrapy.Field()
    remark = scrapy.Field()


class StudentItem(scrapy.Item):
    major_code = scrapy.Field()
    code = scrapy.Field()
    name = scrapy.Field()
    sex = scrapy.Field()
