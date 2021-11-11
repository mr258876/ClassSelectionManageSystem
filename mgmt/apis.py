# -*- coding:utf-8- -*-
from django.http import JsonResponse
from django.shortcuts import render, reverse, redirect
from django.views.decorators.http import require_http_methods

from django.contrib.auth.decorators import login_required, user_passes_test

from django.conf import settings

from .forms import *

import csv
import io
import json

import re

from django.core.paginator import Paginator
from django.core import serializers

# 管理员测试器
def user_is_admin(user):
    return user.is_superuser


# 添加用户API
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
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
        return JsonResponse({"success": True, "code": 200, "message":"操作成功", "data":""})
    else:
        return JsonResponse({"success": False, "code": 400, "message":f.errors, "data":""})


# 导入用户API
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
def import_user_api(request):
    return render(request, "mgmt/add_import_user.html")


# csv解析API
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
def csv_phrase_api(request):
    upload = request.FILES.get("file", None)
    if not upload.name.endswith('.csv'):
        return JsonResponse({"success": False, "code": 400, "message":"非csv文件", "data":""})
    if upload:
        data_text = upload.read().decode("UTF-8")
        io_string = io.StringIO(data_text)
        reader = csv.reader(io_string, delimiter=',')
        row = 0
        data=[]
        for r in reader:
            data.append(r)
            row += 1
            if row > 9:
                break
        return JsonResponse({"success": True, "code": 200, "message":"操作成功", "data":data})
    else:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})
    

# 用户查找API
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
def search_user_api(request):
    kList = ['uid', 'name']

    k = request.POST.get("searchMode", "")
    kw = request.POST.get("keyword", "")
    pN = request.POST.get("page", 1)
    iPP = request.POST.get("itemPerPage", 25)
    
    if k and k in kList:
        if k == 'uid':
            qSet = User.objects.filter(uid__contains=kw).only().values_list('uid', 'name', 'email', 'role', 'is_active').order_by('uid')
            p = Paginator(qSet, iPP)
            # json_response = serializers.serialize('json', list(p.object_list))
            d = json.dumps(list(p.object_list))
        elif k == 'name':
            qSet = User.objects.filter(name__contains=kw).only().values_list('uid', 'name', 'email', 'role', 'is_active').order_by('uid')
            p = Paginator(qSet, iPP)
            # json_response = serializers.serialize('json', list(p.object_list))
            d = json.dumps(list(p.object_list))
        else:
            return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})
        return JsonResponse({"success": True, "code": 200, "message":"操作成功", "data":json.loads(d)})
    else:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})


# 操作用户API
@login_required
@user_passes_test(user_is_admin)
@require_http_methods(['POST'])
def mod_user_api(request):
    uid = request.POST.get("uid", "")
    operation = request.POST.get("operation", "")

    if not uid or not operation:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})
    
    try:
        user = User.object.get(uid=uid)
    except:
        return JsonResponse({"success": False, "code": 400, "message":"用户不存在", "data":""})
    
    if operation == "changePassword":
        pswd = request.POST.get("password", "")
        if re.match(settings.USER_PSWD_PATTERN, pswd):
            user.set_password(pswd)
            return JsonResponse({"success": True, "code": 200, "message":"操作成功", "data":""})
        else:
            return JsonResponse({"success": False, "code": 400, "message":"密码不符合格式", "data":""})
    elif operation == "changeEmail":
        email = request.POST.get("email", "")
        if email:
            user.email = email
            user.save()
            return JsonResponse({"success": True, "code": 200, "message":"操作成功", "data":""})
    elif operation == "setActive":
        active = request.POST.get("active", False)
        user.is_active = bool(active)
        user.save()
        return JsonResponse({"success": True, "code": 200, "message":"操作成功", "data":""})
    else:
        return JsonResponse({"success": False, "code": 400, "message":"操作失败", "data":""})
        

