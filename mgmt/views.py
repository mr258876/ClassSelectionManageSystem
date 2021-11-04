# -*- coding:utf-8- -*-
from django.http import JsonResponse
from django.shortcuts import render, reverse, redirect
from django.views.decorators.http import require_http_methods

from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import AddUserForm

# 管理员测试器
def user_is_admin(user):
    return user.is_superuser


# 主页
@login_required
@user_passes_test(user_is_admin)
def mgmt_home(request):
    return redirect(reverse("add_user"))


# 操作跳转
@login_required
@user_passes_test(user_is_admin)
def switch_operation(request, operation):
    operations = ['add_user', 'import_user',
                  'mod_user', 'set_selection_schedule']
    if operation in operations:
        return eval(operation)(request)


# 增添用户
@login_required
@user_passes_test(user_is_admin)
def add_user(request):
    return render(request, "mgmt/add_import_user.html")


# 更改用户
@login_required
@user_passes_test(user_is_admin)
def mod_user(request):
    return render(request, "mgmt/query_mod_user.html")


# 设置选课时间
@login_required
@user_passes_test(user_is_admin)
def set_selection_schedule(request):
    pass
