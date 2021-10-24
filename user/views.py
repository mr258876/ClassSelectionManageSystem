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


def home(request):
    return render(request, "user/login_home.html")


# 用户登录
@require_http_methods(['GET', 'POST'])
def login(request, *args, **kwargs):
    # HTTP - POST
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)

        if form.is_valid():
            uid = form.cleaned_data["uid"]
            password = form.cleaned_data["password"]

            loginResult = loginVerify(uid, password)
            if loginResult[0]:
                # Login success
                user = loginResult[2]

                request.session['uid'] = user.uid
                request.session['role'] = user.role

                # Check whether user need to complete info
                if request.session.get("needInfoUpdate", "") or isNeedInfoUpdate(user):
                    request.session['needInfoUpdate'] = True
                    return redirect(reverse("update_info"))

                to_url = reverse("course", kwargs={'kind': user.role})
                return redirect(to_url)

            else:
                form.add_error(loginResult[1][0], loginResult[1][1])

            return render(request, 'user/login_detail.html', {'form': form})

    # HTTP - GET
    else:
        if checkLogin(request):
            # Check whether user need to complete info
            if request.session.get("needInfoUpdate", "") or isNeedInfoUpdate(User.objects.get(uid=request.session.get("uid", ""))):
                request.session['needInfoUpdate'] = True
                return redirect(reverse("update_info"))

            to_url = reverse("course", kwargs={
                             'kind': request.session.get("role", "")})
            return redirect(to_url)

        form = UserLoginForm()

        context = {'form': form}
        if request.GET.get('from_url'):
            context['uid'] = request.GET.get('uid')
            context['from_url'] = request.GET.get('from_url')

        return render(request, 'user/login_detail.html', context)


@require_http_methods(['GET'])
def logout(request):
    request.session.flush()
    return render(request, 'user/logout.html')


# 处理注册请求
def register(request):
    func = None

    func = CreateUserView.as_view()

    if func:
        return func(request)
    else:
        return HttpResponse(INVALID_FUNC)


# 创建用户/用户注册
class CreateUserView(CreateView):
    model = User
    form_class = UserRegisterForm
    # fields = "__all__"
    template_name = "user/register.html"
    success_url = "login"

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            self.object = None
            return self.form_invalid(form)

    def form_valid(self, form):
        # Create, but don't save the new student instance. 创建用户对象，但暂时不提交对象
        new_user = form.save(commit=False)

        # Set User Role
        uid = form.cleaned_data['uid']
        if uid[0] == '1':
            new_user.role = 'student'
        elif uid[0] == '3':
            new_user.role = 'teacher'
        elif uid[0] == '8':
            new_user.role = 'dept'
        elif uid[0] == '0':
            new_user.role = 'admin'

        # Save the new instance. 保存用户对象
        new_user.save()
        # Now, save the many-to-many data for the form. 保存多对多关系
        form.save_m2m()

        # Attach Role Object
        if new_user.role == 'student':
            roleObject = Student(user=new_user)
            roleObject.save()
            new_user.student = roleObject
        elif new_user.role == 'teacher':
            roleObject = Teacher(user=new_user)
            roleObject.save()
            new_user.teacher = roleObject

        self.request.session['needInfoUpdate'] = True

        self.object = new_user

        from_url = "register"
        base_url = reverse(self.get_success_url(),
                           kwargs={'role': new_user.role})
        return redirect(base_url + '?uid=%s&from_url=%s' % (uid, from_url))


# 处理密码邮箱更新请求
def update_security(request):
    func = None

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
def update_info(request):
    func = None

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
