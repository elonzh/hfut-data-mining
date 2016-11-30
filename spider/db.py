# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import pymongo
from pymongo import UpdateOne

from .log import logger

COLLECTIONS = ('term', 'major', 'course', 'plan', 'class', 'student', 'class_student')


def init_db(db):
    # 初始化数据库
    # http://api.mongodb.com/python/3.3.1/api/pymongo/collection.html#pymongo.collection.Collection.create_index
    term_idx = ('学期代码', pymongo.ASCENDING)
    major_idx = ('专业代码', pymongo.ASCENDING)
    course_idx = ('课程代码', pymongo.ASCENDING)
    class_idx = ('教学班号', pymongo.ASCENDING)
    student_idx = ('学号', pymongo.ASCENDING)
    db['term'].create_index([term_idx], unique=True)
    db['major'].create_index([major_idx], unique=True)
    db['course'].create_index([course_idx], unique=True)
    db['plan'].create_index([term_idx, major_idx, course_idx], unique=True)
    db['class'].create_index([term_idx, course_idx, class_idx], unique=True)
    db['student'].create_index([student_idx], unique=True)
    db['class_student'].create_index([term_idx, course_idx, class_idx, student_idx], unique=True)
    return db


def report_db(db):
    pieces = [' Database Reporter '.center(72, '=')]
    for k in COLLECTIONS:
        pieces.append('Collection %s: %d' % (k, db[k].count()))
    msg = '\n'.join(pieces)
    logger.info(msg)


def InsertOnNotExist(query, document):
    # https://docs.mongodb.com/manual/reference/operator/update/setOnInsert/#setoninsert
    return UpdateOne(query, {'$setOnInsert': document}, True)
