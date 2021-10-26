# usr/bin/env python3
# -*- coding:utf-8- -*-
import random

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse, redirect
from django.views.generic import CreateView, UpdateView
from django.views.decorators.http import require_http_methods

from constants import INVALID_KIND, INVALID_FUNC
from user.forms import UserLoginForm, UserRegisterForm, UserUpdateForm, TeaUpdateForm, StuUpdateForm
from user.models import User, Student, Teacher
from user.util import checkLogin, loginVerify, isNeedInfoUpdate

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required


# 处理登录请求
@require_http_methods(['GET', 'POST'])
def login(request, *args, **kwargs):
    func = UserLoginView.as_view()
    if func:
        return func(request)

# 登录视图


class UserLoginView(LoginView):
    template_name = 'user/login_detail.html'
    authentication_form = UserLoginForm


# 处理登出请求
@login_required
@require_http_methods(['GET'])
def logout(request):
    func = UserLogoutView.as_view()
    if func:
        return func(request)

# 登出视图
class UserLogoutView(LogoutView):
    template_name = 'user/logout.html'


# 处理注册请求
@require_http_methods(['GET', 'POST'])
def register(request):
    func = UserCreationView.as_view()

    if func:
        return func(request)


# 创建用户/用户注册
class UserCreationView(CreateView):
    form_class = UserRegisterForm
    template_name = "user/register.html"
    success_url = "info"

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            self.object = None
            return self.form_invalid(form)

    def form_valid(self, form):
        new_user = form.save()
        # # Create, but don't save the new student instance. 创建用户对象，但暂时不提交对象以进行操作
        # new_user = form.save(commit=False)

        # # Save the new instance. 保存用户对象
        # new_user.save()
        # # Now, save the many-to-many data for the form. 保存多对多关系
        # form.save_m2m()

        self.request.session['needInfoUpdate'] = True

        self.object = new_user

        self.request.session['title'] = '注册成功'
        self.request.session['info'] = '您的用户名是' + form.cleaned_data['username']
        self.request.session['next'] = 'login'
        url = reverse(self.get_success_url())
        return redirect(url)


# 处理密码邮箱更新请求
@login_required
def update_security(request):
    func = UpdateUserView.as_view()

    if func:
        pk = request.session.get("uid", "")
        if pk:
            context = {
                "name": request.session.get("name", ""),
                "role": request.session.get("role", ""),
            }
            return func(request, pk=pk, context=context)
        else:
            return redirect(reverse("login"))
    else:
        return HttpResponse(INVALID_KIND)


# 用户密码更新
class UpdateUserView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "user/update_security.html"

    def get_context_data(self, **kwargs):
        context = super(UpdateUserView, self).get_context_data(**kwargs)
        context.update(kwargs)
        return context

    def get_success_url(self):
        return reverse("course", kwargs={"role": "student"})


# 处理教师学生信息更新请求
@login_required
def update_info(request):
    role = request.session.get("role", "")

    if role == "student":
        func = UpdateStudentView.as_view()
    elif role == "teacher":
        func = UpdateTeacherView.as_view()

    if func:
        pk = request.session.get("uid", "")
        if pk:
            context = {
                "name": request.session.get("name", ""),
                "role": request.session.get("role", ""),
                "force": request.session.get("needInfoUpdate", ""),
            }
            return func(request, pk=pk, context=context)
        else:
            return redirect(reverse("login"))
    else:
        return HttpResponse(INVALID_KIND)


# 学生信息更新
class UpdateStudentView(UpdateView):
    model = Student
    form_class = StuUpdateForm
    template_name = "user/update_info.html"

    def get_context_data(self, **kwargs):
        context = super(UpdateStudentView, self).get_context_data(**kwargs)
        context.update(kwargs)
        context["force"] = self.request.session.get("needInfoUpdate", "")
        context["role"] = "student"
        return context

    def get_success_url(self):
        return reverse("course", kwargs={"role": "student"})


# 教师信息更新
class UpdateTeacherView(UpdateView):
    model = Teacher
    form_class = TeaUpdateForm
    template_name = "user/update_info.html"

    def get_context_data(self, **kwargs):
        context = super(UpdateTeacherView, self).get_context_data(**kwargs)
        context.update(kwargs)
        context["force"] = self.request.session.get("needInfoUpdate", "")
        context["role"] = "teacher"
        return context

    def get_success_url(self):
        return reverse("course", kwargs={"role": "teacher"})
