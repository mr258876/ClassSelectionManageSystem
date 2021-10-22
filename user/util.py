# usr/bin/env python
# -*- coding:utf-8- -*-
from django.http.response import HttpResponse
from django.shortcuts import reverse, redirect

from constants import *
from user.models import Student, Teacher, User


def check_login(func):
    # the func method must have the second parameter kind.
    def _check(*args, **kwargs):
        request = args[1]
        cookie_kind = request.session.get('role', '')
        if cookie_kind not in ["S", "T", "O", "A"]:
            # Not logged in
            to_url = reverse("login")
            return redirect(to_url)
        elif len(args) >= 2:
            # the second parameter must be kind
            kind = args[1]
            if kind == cookie_kind:
                return func(*args, **kwargs)
            else:
                return HttpResponse(ILLEGAL_KIND)
        return HttpResponse(INVALID_URL)

    return _check


def get_user(request, role):
    """

    :param request:
    :param role: user role, 'S', 'T', 'O', or 'A'
    :return: return Teacher instance or Student instance
    """
    if request.session.get('role', '') != role or role not in ["S", "T", "O", "A"]:
        return None

    if len(request.session.get('uid', '')) != 10:
        return None

    uid = request.session.get('uid')
    # 找到对应用户
    userSet = User.objects.filter(uid=uid)
    if userSet.count() == 0:
        return None
    return userSet[0]


