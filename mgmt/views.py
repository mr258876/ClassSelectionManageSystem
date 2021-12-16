# -*- coding:utf-8- -*-
from django.http import JsonResponse
from django.shortcuts import render, reverse, redirect
from django.views.decorators.http import require_http_methods

from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import AddUserForm

# 用户具有管理权限
def user_mgmtable(user):
    return user.role == 'dept' or user.is_superuser

# 管理员测试器
def user_is_admin(user):
    return user.is_superuser


# 主页
@login_required
@user_passes_test(user_mgmtable)
def mgmt_home(request):
    if request.user.is_superuser:
        return redirect(reverse("add_user"))
    elif hasattr(request.user, 'department'):
        return render(request, "mgmt/mod_dept_info.html", {'dept_no': request.user.department})
    else:
        return render(request, "info.html", {'title': '权限错误', 'info': '您没有操作任何院系的权限，请联系管理员', 'next': 'logout'})


# 操作跳转
@login_required
@user_passes_test(user_mgmtable)
def switch_operation(request, operation):
    operations = ['add_user', 'mod_user', 
                    'add_dept', 'mod_dept',
                    'semester_settings']
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
def semester_settings(request):
    return render(request, "mgmt/semester_settings.html")


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