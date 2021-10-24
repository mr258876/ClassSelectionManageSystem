# usr/bin/env python3
# -*- coding:utf-8- -*-
from django.db import models
from django.db.models.deletion import CASCADE

from django.core import serializers

class User(models.Model):
    roles = [
        ("student", "学生"),
        ("teacher", "教师"),
        ("dept", "院系"),
        ("admin", "系统管理员")
    ]

    uid = models.CharField(max_length=8, primary_key=True)
    password = models.CharField(max_length=40, null=False)
    email = models.EmailField(max_length=32, verbose_name="邮箱")
    role = models.CharField(max_length=7, choices=roles, null=False, verbose_name="角色")


class Student(models.Model):
    genders = [
        ("m", "男"),
        ("f", "女")
    ]

    user = models.OneToOneField(User, on_delete=CASCADE, primary_key=True)
    name = models.CharField(max_length=50, verbose_name="姓名")
    gender = models.CharField(max_length=1, choices=genders, verbose_name="性别")
    birthday = models.DateField(null=True, verbose_name="生日")
    grade = models.CharField(max_length=4, verbose_name="年级")
    number = models.CharField(max_length=6, verbose_name="班级学号")

    def get_id(self):
        return self.grade + self.number

    def __str__(self):
        return "%s (%s)" % (self.grade + self.number, self.name)


class Teacher(models.Model):
    genders = [
        ("m", "男"),
        ("f", "女")
    ]

    user = models.OneToOneField(User, on_delete=CASCADE, primary_key=True)
    name = models.CharField(max_length=50, verbose_name="姓名")
    gender = models.CharField(max_length=1, choices=genders, verbose_name="性别")
    birthday = models.DateField(null=True, verbose_name="生日")
    department_no = models.CharField(max_length=3, verbose_name="院系号")
    info = models.CharField(help_text='不要超过250字', max_length=255, verbose_name='教师简介')