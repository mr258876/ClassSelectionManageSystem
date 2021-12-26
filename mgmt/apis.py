# -*- coding:utf-8- -*-
from django.http import JsonResponse
from django.shortcuts import render, reverse, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie

from django.contrib.auth.decorators import login_required, user_passes_test

from django.conf import settings

from .forms import *

import csv
import io
import json
import datetime

import re

from django.core.paginator import Paginator
from django.core import serializers

from course.models import Department
from .models import Semester


# 管理员测试器
def user_is_admin(user):
    return user.is_superuser

# 院系权限测试器
def user_is_dept(user):
    return user.role == 'dept' and hasattr(user, 'department')


#######################################
# 用户API

# 添加用户API
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def add_user_api(request):
    data = {'username': request.POST.get('username', 0),
            'password1': request.POST.get('password', 0),
            'password2': request.POST.get('password', 0),
            'email': request.POST.get('email', 0),
            'user_role': request.POST.get('auth', 0),
            'name': request.POST.get('name', "")
            }
    f = AddUserForm(data)

    if f.is_valid():
        f.save()
        return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})
    else:
        return JsonResponse({"success": False, "code": 400, "message": f.errors, "data": ""})


# 导入用户API
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def import_user_api(request):
    return render(request, "mgmt/add_import_user.html")


# csv解析API
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
def csv_phrase_api(request):
    upload = request.FILES.get("file", None)
    if not upload.name.endswith('.csv'):
        return JsonResponse({"success": False, "code": 400, "message": "非csv文件", "data": ""})
    if upload:
        data_text = upload.read().decode("UTF-8")
        io_string = io.StringIO(data_text)
        reader = csv.reader(io_string, delimiter=',')
        row = 0
        data = []
        for r in reader:
            data.append(r)
            row += 1
            if row > 9:
                break
        return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": data})
    else:
        return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})


# 用户查找API
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def search_user_api(request):
    kList = ['uid', 'name']

    k = request.POST.get("searchMode", "")
    kw = request.POST.get("keyword", "")
    pN = request.POST.get("page", 1)
    iPP = request.POST.get("itemPerPage", 25)

    if k and k in kList:
        qSet = None
        if k == 'uid':
            qSet = User.objects.filter(uid__contains=kw).only().values_list(
                'uid', 'name', 'email', 'role', 'is_active').order_by('uid')
        elif k == 'name':
            qSet = User.objects.filter(name__contains=kw).only().values_list(
                'uid', 'name', 'email', 'role', 'is_active').order_by('uid')
        else:
            return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})
        p = Paginator(qSet, iPP)
        # json_response = serializers.serialize('json', list(p.object_list))
        d = json.dumps(list(p.page(pN)))
        d = json.loads(d)
        plist = p.get_elided_page_range(pN, on_each_side=2, on_ends=1)
        pl = json.dumps(list(plist))
        pl = json.loads(pl)
        return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": {'users': d, 'plist': pl, 'page': pN}})
    else:
        return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})


# 操作用户API
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def mod_user_api(request):
    uid = request.POST.get("uid", "")
    operation = request.POST.get("operation", "")

    if not uid or not operation:
        return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})

    try:
        user = User.objects.get(uid=uid)
    except:
        return JsonResponse({"success": False, "code": 400, "message": "用户不存在", "data": ""})

    if operation == "changePassword":
        pswd = request.POST.get("password", "")
        if re.match(settings.USER_PSWD_PATTERN, pswd):
            user.set_password(pswd)
            return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})
        else:
            return JsonResponse({"success": False, "code": 400, "message": "密码不符合格式", "data": ""})
    elif operation == "changeEmail":
        email = request.POST.get("email", "")
        if email:
            user.email = email
            user.save()
            return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})
    elif operation == "setActive":
        active = request.POST.get("active", False)
        if active == "true":
            user.is_active = True
        else:
            user.is_active = False
        user.save()
        return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})
    else:
        return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})


#######################################
# 院系API

# 新建院系
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def add_dept_api(request):
    d_no = request.POST.get("deptId", "")
    d_name = request.POST.get("deptName", "")
    d_user = request.POST.get("deptUser", "")

    dept_set = Department.objects.filter(dept_no=d_no)
    if len(dept_set) > 0:
        return JsonResponse({"success": False, "code": 400, "message": "院系ID已存在", "data": ""})

    dept_user = None
    if d_user:
        user_set = User.objects.filter(uid=d_user)
        if len(user_set) == 0:
            return JsonResponse({"success": False, "code": 400, "message": "用户id不存在", "data": ""})
        if user_set[0].role != 'dept':
            return JsonResponse({"success": False, "code": 400, "message": "用户权限错误", "data": ""})
        dept_user = user_set[0]

    try:
        dept_user.name = d_name
        dept_user.save()
        dept = Department(dept_no=d_no, dept_name=d_name,
                          dept_user=dept_user)
        dept.save()
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "创建失败", "data": str(e)})
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})


# 修改院系信息
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def mod_dept_api(request):
    d_no = request.POST.get("deptId", "")
    d_name = request.POST.get("deptName", "")
    d_user = request.POST.get("deptUser", "")

    dept_set = Department.objects.filter(dept_no=d_no)
    if len(dept_set) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "院系ID不存在", "data": ""})

    user_set = User.objects.filter(uid=d_user)
    if len(user_set) == 0:
        return JsonResponse({"success": False, "code": 400, "message": "用户id不存在", "data": ""})
    if user_set[0].role != 'dept':
        return JsonResponse({"success": False, "code": 400, "message": "用户权限错误", "data": ""})
    dept_user = user_set[0]

    try:
        # 新assign的用户改名
        dept_user.name = d_name
        dept_user.save()

        dept = dept_set[0]

        # 以前的用户名字删掉
        dept.dept_user.name = None

        dept.dept_no = d_no
        dept.dept_name = d_name
        dept.dept_user = dept_user
        dept.save()
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "创建失败", "data": str(e)})
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})


# 查询院系
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def search_dept_api(request):
    kList = ['deptId', 'deptName']

    k = request.POST.get("searchMode", "")
    kw = request.POST.get("keyword", "")
    pN = request.POST.get("page", 1)
    iPP = request.POST.get("itemPerPage", 25)

    if k and k in kList:
        qSet = None
        if k == 'deptId':
            qSet = Department.objects.filter(dept_no__contains=kw).only().values_list(
                'dept_no', 'dept_name', 'dept_user').order_by('dept_no')
        elif k == 'deptName':
            qSet = Department.objects.filter(dept_name__contains=kw).only().values_list(
                'dept_no', 'dept_name', 'dept_user').order_by('dept_no')
        else:
            return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})
        p = Paginator(qSet, iPP)
        # json_response = serializers.serialize('json', list(p.object_list))
        d = json.dumps(list(p.object_list))
        d = json.loads(d)
        plist = p.get_elided_page_range(pN, on_each_side=2, on_ends=1)
        pl = json.dumps(list(plist))
        pl = json.loads(pl)
        return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": {'dept': d, 'plist': pl, 'page': pN}})
    else:
        return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": ""})


#######################################
# 学期设置API

# 创建学期
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def add_semester_api(request):
    s_name = request.POST.get("name", "")
    s_year = request.POST.get("year", "")
    s_no = request.POST.get("no", "")
    start_date = request.POST.get("startDate", "")
    end_date = request.POST.get("endDate", "")
    select_start = request.POST.get("selectStarts", "")
    select_end = request.POST.get("selectEnds", "")

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    if len(select_start) == 19:
        select_start = datetime.datetime.strptime(select_start, "%Y-%m-%dT%H:%M:%S")
    else:
        select_start = datetime.datetime.strptime(select_start, "%Y-%m-%dT%H:%M")
    if len(select_end) == 19:
        select_end = datetime.datetime.strptime(select_end, "%Y-%m-%dT%H:%M:%S")
    else:
        select_end = datetime.datetime.strptime(select_end, "%Y-%m-%dT%H:%M")
    if start_date >= end_date or select_start >= select_end:
        return JsonResponse({"success": False, "code": 400, "message": "创建失败", "data": '时间错误'})

    # s_list = Semester.objects.filter(start_time__gte=start_date).filter(end_time__lte=end_date)

    try:
        seme = Semester(semester_name=s_name, semester_year=s_year, semester_no=s_no,
                        start_time=start_date, end_time=end_date, select_start=select_start, select_end=select_end)
        seme.save()
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "创建失败", "data": str(e)})
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})


# 查询学期
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def search_semester_api(request):
    kw = request.POST.get("keyword", "")
    pN = request.POST.get("page", 1)
    iPP = request.POST.get("itemPerPage", 25)

    qSet = Semester.objects.filter(semester_year__contains=kw).only().values_list(
        'id', 'semester_name', 'semester_year', 'semester_no', 'start_time', 'end_time', 'select_start', 'select_end').order_by('start_time')
    p = Paginator(qSet, iPP)
    
    data_list = []
    for row in p.object_list:
        # l = {'id': row[0], 'semester_name': row[1], 'semester_year': row[2], 'semester_no': row[3]}
        # l['start_time'] = str(row[4])
        # l['end_time'] = str(row[5])
        # l['select_start'] = str(row[6])
        # l['select_end'] = str(row[7])
        l = [row[i] for i in range(4)]
        l.append(row[4])
        l.append(row[5])
        l.append(row[6].strftime("%Y-%m-%d %H:%M:%S"))
        l.append(row[7].strftime("%Y-%m-%d %H:%M:%S"))
        data_list.append(l)
    # d = json.loads(data_list)
    plist = p.get_elided_page_range(pN, on_each_side=2, on_ends=1)
    pl = json.dumps(list(plist))
    pl = json.loads(pl)
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": {'semester': data_list, 'plist': pl, 'page': pN}})


# 修改学期
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
@ensure_csrf_cookie
def mod_semester_api(request):
    s_id = request.POST.get("id", "")
    s_name = request.POST.get("name", "")
    s_year = request.POST.get("year", "")
    s_no = request.POST.get("no", "")
    start_date = request.POST.get("startDate", "")
    end_date = request.POST.get("endDate", "")
    select_start = request.POST.get("selectStarts", "")
    select_end = request.POST.get("selectEnds", "")

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    if len(select_start) == 19:
        select_start = datetime.datetime.strptime(select_start, "%Y-%m-%dT%H:%M:%S")
    else:
        select_start = datetime.datetime.strptime(select_start, "%Y-%m-%dT%H:%M")
    if len(select_end) == 19:
        select_end = datetime.datetime.strptime(select_end, "%Y-%m-%dT%H:%M:%S")
    else:
        select_end = datetime.datetime.strptime(select_end, "%Y-%m-%dT%H:%M")
    if start_date >= end_date or select_start >= select_end:
        return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": '输入时间错误'})

    s_list = Semester.objects.filter(id=s_id).only()
    if len(s_list):
        seme = s_list[0]
    else:
        return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": '学期不存在'})

    try:
        seme.semester_name=s_name
        seme.semester_year=s_year
        seme.semester_no=s_no
        seme.start_time=start_date
        seme.end_time=end_date
        seme.select_start=select_start
        seme.select_end=select_end
        seme.save()
    except Exception as e:
        return JsonResponse({"success": False, "code": 400, "message": "操作失败", "data": str(e)})
    return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": ""})


# 查询当前学期
@login_required
@require_http_methods(['POST'])
@ensure_csrf_cookie
def get_semester_api(request):
    s_list = Semester.objects.filter(start_time__lte=datetime.date.today()).filter(end_time__gte=datetime.date.today())
    if len(s_list) == 0:
        s_list = Semester.objects.filter(start_time__gte=datetime.date.today()).order_by('start_time')
    else:
        return JsonResponse({"success": True, "code": 200, "message": "操作成功", "data": {'id': s_list[0].id, 'name': s_list[0].semester_name}})
