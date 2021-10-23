# usr/bin/env python
# -*- coding:utf-8- -*-
from django.http.response import HttpResponse
from django.shortcuts import reverse, redirect

from constants import *
from user.models import Student, Teacher, User


# 检查登录状态
def checkLogin(request):
    uid = request.session.get('uid', '')
    role = request.session.get('role', '')
    if not uid or not role:
        return False
    
    userSet = User.objects.filter(uid=uid)
    if userSet.count() == 0:
        return False

    if userSet[0].role != role:
        return False

    return True


# 登陆验证
def loginVerify(uid, password):
    if len(uid) != 8:
        return (False, ("uid", "账号长度必须为8"), None)
    
    userSet = User.objects.filter(uid=uid)
    if userSet.count() == 0:
        return (False, ("password", "用户名或密码错误"), None)

    user = userSet[0]
    if password == user.password:
        return (True, None, user)

    return (False, ("password", "用户名或密码错误"), None)


# 检查是否需要更新个人信息
def isNeedInfoUpdate(user):
    if user.role == 'dept' or user.role == 'admin':
        return False
    
    roleObject = getattr(user, user.role)
    if not roleObject.name or not roleObject.gender or not roleObject.birthday:
        return True
    return False


# 获取用户对象
def getUser(request):
    """

    :param request:
    :return: return Teacher instance or Student instance
    """
    if len(request.session.get('uid', '')) != 8:
        return None

    uid = request.session.get('uid')
    # 找到对应用户
    userSet = User.objects.filter(uid=uid)
    if userSet.count() == 0:
        return None
    return userSet[0]


# 获取用户身份对象
def getRoleObject(request, role):
    """

    :param request:
    :param role: user role, 'student', 'teacher', 'operator', 'admin'
    :return: return Student, Teacher or Dept instance
    """

    if len(request.session.get('uid', '')) != 8:
        return None

    uid = request.session.get('uid')
    # 找到对应用户
    userSet = User.objects.filter(uid=uid)
    if userSet.count() == 0:
        return None
    if hasattr(userSet[0], role):
        return getattr(userSet[0], role)
    else:
        return None