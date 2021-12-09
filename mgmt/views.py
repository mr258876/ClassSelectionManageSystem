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
    operations = ['add_user', 'mod_user', 
                    'add_dept', 'mod_dept',
                    'set_selection_schedule']
    if operation in operations:
        return eval(operation)(request)


#######################################
# 用户管理

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


#######################################
# 系统管理

# 设置选课时间
@login_required
@user_passes_test(user_is_admin)
def set_selection_schedule(request):
    pass


#######################################
# 院系管理

# 新建院系
@login_required
@user_passes_test(user_is_admin)
def add_dept(request):
    return render(request, "mgmt/add_dept.html")


# 修改院系
@login_required
@user_passes_test(user_is_admin)
def mod_dept(request):
    return render(request, "mgmt/query_mod_dept.html")


# 修改院系具体信息
@login_required
@user_passes_test(user_is_admin)
def mod_dept_info(request, dept_no):
    return render(request, "mgmt/mod_dept_info.html", {'dept_no': dept_no})