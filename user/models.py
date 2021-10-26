# usr/bin/env python3
# -*- coding:utf-8- -*-
from django.conf import settings
from django.db import models
from django.db.models.deletion import CASCADE

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


# 用户类管理器
class UserManager(BaseUserManager):
    def _create_user(self, uid, password=None, email=None, user_role=None):
        if not uid:
            raise ValueError('Users must have an uid')

        if not user_role:
            if uid[0] == '1' or uid[0] == '2':
                user_role = 'student'
            elif uid[0] == '3':
                user_role = 'teacher'
            elif uid[0] == '8':
                user_role = 'dept'
            else:
                raise ValueError('Unexpected uid')

        user = self.model(
            uid = uid,
            email = self.normalize_email(email),
            role = user_role,
        )

        user.set_password(password)
        if user_role == 'admin':
            user.is_admin = True
        user.save(using=self._db)

        # Attach Role Object
        if user.role == 'student':
            roleObject = Student(user=user)
            roleObject.save()
            user.student = roleObject
        elif user.role == 'teacher':
            roleObject = Teacher(user=user)
            roleObject.save()
            user.teacher = roleObject

        return user
    
    def create_user(self, uid, password=None, email=None, user_role=None):
        return self._create_user(uid, password, email, user_role)
    
    def create_superuser(self, uid, password, email=None, user_role=None):
        return self._create_user(uid, password, email, user_role='admin')


# 继承AbstractBaseUser以及PermissionsMixin以利用django自带用户登录以及权限管理
class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    roles = [
        ("student", "学生"),
        ("teacher", "教师"),
        ("dept", "院系"),
        ("admin", "系统管理员")
    ]

    uid = models.CharField(max_length=8, primary_key=True)
    USERNAME_FIELD = 'uid'

    email = models.EmailField(max_length=32, verbose_name="邮箱")
    EMAIL_FIELD = 'email'

    role = models.CharField(max_length=7, choices=roles, null=False, verbose_name="角色")
    need_complete_info = models.BooleanField(default=True, verbose_name="是否需要更新个人信息")
    REQUIRED_FIELD = ["role", "need_complete_info"]

    is_active = models.BooleanField(default=True, verbose_name="用户状态")
    is_superuser = models.BooleanField(default=False, verbose_name="是否为管理员")

    def __str__(self):
        return self.uid



# 学生类
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


# 教师类
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