# usr/bin/env python3
# -*- coding:utf-8- -*-
from django.db import models
from django.db.models.deletion import CASCADE


class User(models.Model):
    roles = [
        ("S", "学生"),
        ("T", "教师"),
        ("O", "院系"),
        ("A", "系统管理员")
    ]

    uid = models.CharField(max_length=8, primary_key=True)
    password = models.CharField(max_length=40)
    role = models.CharField(max_length=1, choices=roles, verbose_name="角色")


class Student(models.Model):
    gender = [
        ("m", "男"),
        ("f", "女")
    ]

    uid = models.ForeignKey(User, on_delete=CASCADE)
    name = models.CharField(max_length=50, verbose_name="姓名")
    gender = models.CharField(max_length=10, choices=gender, default='m', verbose_name="性别")
    birthday = models.DateField(verbose_name="生日")
    email = models.EmailField(verbose_name="邮箱")
    grade = models.CharField(max_length=4, verbose_name="年级")
    number = models.CharField(max_length=6, verbose_name="年级子学号")

    def get_id(self):
        return self.grade + self.number

    def __str__(self):
        return "%s (%s)" % (self.grade + self.number, self.name)


class Teacher(models.Model):
    genders = [
        ("m", "男"),
        ("f", "女")
    ]

    uid = models.ForeignKey(User, on_delete=CASCADE)
    name = models.CharField(max_length=50, verbose_name="姓名")
    gender = models.CharField(max_length=10, choices=genders, default='m', verbose_name="性别")
    birthday = models.DateField(verbose_name="生日")
    email = models.EmailField(verbose_name="邮箱")
    info = ('info', models.CharField(help_text='不要超过250字', max_length=255, verbose_name='教师简介'))
    department_no = models.CharField(max_length=3, verbose_name="院系号")
    number = models.CharField(max_length=7, verbose_name="院内编号")
    password = models.CharField(max_length=30, verbose_name="密码")



