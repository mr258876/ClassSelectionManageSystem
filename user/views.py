# usr/bin/env python3
# -*- coding:utf-8- -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse, redirect
from django.views.generic import CreateView, UpdateView
from django.views.decorators.http import require_http_methods

from .forms import UserLoginForm, UserRegisterForm, UserUpdateForm, TeaUpdateForm, StuUpdateForm
from .models import User, Student, Teacher

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required


# 处理登录请求
@require_http_methods(['GET', 'POST'])
def login(request, *args, **kwargs):
    if request.user.is_authenticated:
        return redirect('course')

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

# 创建用户/用户注册视图
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

        self.object = new_user

        # 使用session传参
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
        return func(request, pk=request.user.uid)

# 用户密码更新视图
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
    uid = request.user.uid
    role = request.user.role
    func = None

    if role == "student":
        func = UpdateStudentView.as_view()
    elif role == "teacher":
        func = UpdateTeacherView.as_view()

    if func:
        return func(request, pk=uid)
    else:
        # 使用session传参
        request.session['title'] = '提示'
        request.session['info'] = '您没有可更改的个人信息'
        request.session['next'] = 'course'
        return redirect('info')

# 学生信息更新视图
class UpdateStudentView(UpdateView):
    model = Student
    form_class = StuUpdateForm
    template_name = "user/update_info.html"

    # 获取url参数
    def get_context_data(self, **kwargs):
        context = super(UpdateStudentView, self).get_context_data(**kwargs)
        context.update(kwargs)
        context["force"] = self.request.user.need_complete_info
        return context
    
    def get_success_url(self):
        return reverse("course", kwargs={"role": "student"})

    def form_valid(self, form):
        self.object.user.need_complete_info = False
        self.object.user.name = form.cleaned_data['name']
        self.object.user.save()
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())

# 教师信息更新视图
class UpdateTeacherView(UpdateView):
    model = Teacher
    form_class = TeaUpdateForm
    template_name = "user/update_info.html"

    # 获取url参数
    def get_context_data(self, **kwargs):
        context = super(UpdateTeacherView, self).get_context_data(**kwargs)
        context.update(kwargs)
        context["force"] = self.request.user.need_complete_info
        return context
    
    def get_success_url(self):
        return reverse("course", kwargs={"role": "teacher"})
    
    def form_valid(self, form):
        self.object.user.need_complete_info = False
        self.object.user.name = form.cleaned_data['name']
        self.object.user.save()
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())