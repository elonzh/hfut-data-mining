# -*- coding:utf-8 -*-
from django.db import models

class StudentModel(models.Model):
    class Meta:
        verbose_name = '学生'
    code = models.CharField('学号')
    name = models.CharField('姓名')
    sex = models.CharField('性别')

class MajorModel(models.Model):
    class Meta:
        verbose_name = '专业'
    code = models.CharField('专业代码')
    name = models.CharField('专业名称')

class TermModel(models.Model):
    class Meta:
        verbose_name = '学期'
    code = models.CharField('学期代码')
    name = models.CharField('学期名称')

class CourseModel(models.Model):
    class Meta:
        verbose_name = '课程'
    code = models.CharField('课程代码')
    name = models.CharField('课程名称')
    credit = models.FloatField('学分')
    hours = models.IntegerField('学时')
    belong_to = models.CharField('开课单位')

class TeachingPlanModel(models.Model):
    class Meta:
        verbose_name = '教学计划'
        default_related_name = 'teaching_plan'
        unique_together = (('term', 'course', 'major'),)

    term = models.ForeignKey(TermModel)
    course = models.ForeignKey(CourseModel)
    major = models.ForeignKey(MajorModel)

class TeachingClassModel(models.Model):
    class Meta:
        verbose_name = '教学班级'
        default_related_name = 'teaching_classes'
        unique_together = (('term', 'course', 'number'),)
    term = models.ForeignKey(TermModel)
    course = models.ForeignKey(CourseModel)
    students = models.ManyToManyField(StudentModel)
    course_type = models.CharField('课程类型')
    exam_type = models.CharField('考核类型')
    number = models.CharField('教学班号')
    campus = models.CharField('校区')
    # weeks = ArrayField(base_field=models.PositiveSmallIntegerField())
    weeks = models.CharField('起止周')
    time_and_place = models.CharField('时间地点')
    size = models.IntegerField('班级容量')
    sex_limit = models.CharField('性别限制')
    preferred_scope = models.CharField('优选范围')
    forbidden_scope = models.CharField('禁选范围')
    remark = models.TextField('备注')
