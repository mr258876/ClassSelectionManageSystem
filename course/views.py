from django.http.response import HttpResponse
from django.shortcuts import render, reverse, redirect

from django.utils import timezone

from django.contrib.auth.decorators import login_required, user_passes_test

from mgmt.util import get_now_elect_semester


#######################################
# 权限测试器

# 用户具有管理权限
def user_classable(user):
    return user.role == 'student' or user.role == 'teacher'

# 教师权限测试器
def user_is_teacher(user):
    return user.role == 'teacher'

# 学生权限测试器
def user_is_student(user):
    return user.role == 'student'


# 主页
@login_required
def home(request):
    if request.user.need_complete_info:
        return redirect(reverse("update_info"))
    
    return render(request, "course/course_home.html")

# 选课页面
@login_required
@user_passes_test(user_is_student)
def elect(request):
    sem = get_now_elect_semester()
    if not sem:
        return render(request, "info.html", {'title': '选课未开放', 'info': '当前不在选课时间范围内', 'next': 'course'})
    return render(request, "course/elect.html", {'semester': sem.id})

# 我的课程
@login_required
@user_passes_test(user_classable)
def my_classes(request):
    return render(request, "course/course_home.html")