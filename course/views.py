from django.http.response import HttpResponse
from django.shortcuts import render, reverse, redirect

from django.utils import timezone

from django.contrib.auth.decorators import login_required


# 主页
@login_required
def home(request):
    if request.user.need_complete_info:
        return redirect(reverse("update_info"))
    
    return render(request, "course/course_home.html")