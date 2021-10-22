# usr/bin/env python3
# -*- coding:utf-8- -*-
import random

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse, redirect
from django.views.generic import CreateView, UpdateView

from constants import INVALID_KIND
from user.forms import UserLoginForm, UserRegisterForm, UserUpdateForm, TeaUpdateForm, StuUpdateForm
from user.models import User, Student, Teacher


def home(request):
    return render(request, "user/login_home.html")


# def login(request, kind)
def login(request, *args, **kwargs):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)

        if form.is_valid():
            uid = form.cleaned_data["uid"]
            if len(uid) != 8:
                form.add_error("uid", "账号长度必须为8")
            else:
                userSet = User.objects.filter(uid=uid)
                if userSet.count() == 0:
                    form.add_error("password", "用户名或密码错误")
                else:
                    user = userSet[0]
                    if form.cleaned_data["password"] != user.password:
                        form.add_error("password", "用户名或密码错误")
                    else:
                        request.session['uid'] = user.uid
                        request.session['role'] = user.role
                        # successful login
                        if user.role == 'S':
                            kind = 'student'
                        elif user.role == 'T':
                            kind == 'teacher'
                        to_url = reverse("course", kwargs={'kind': kind})
                        return redirect(to_url)

            return render(request, 'user/login_detail.html', {'form': form})
    else:
        form = UserLoginForm()
        
        context = {'form': form}
        if request.GET.get('from_url'):
            context['from_url'] = request.GET.get('from_url')

        return render(request, 'user/login_detail.html', context)


def logout(request):
    if request.session.get("user", ""):
        del request.session["user"]
    if request.session.get("uid", ""):
        del request.session["uid"]
    return redirect(reverse("login"))


# 处理注册请求
def register(request):
    func = None

    func = CreateUserView.as_view()
    request.session['needInfoUpdate'] = True

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
        # Create, but don't save the new student instance.
        new_user = form.save(commit=False)
        # Set User Role
        uid = form.cleaned_data['uid']
        if uid[0] == '1':
            new_user.role = 'S'
        elif uid[0] == '3':
            new_user.role = 'T'
        elif uid[0] == '8':
            new_user.role = 'O' 
        elif uid[0] == '0':
            new_user.role = 'A'
        # Save the new instance.
        new_user.save()
        # Now, save the many-to-many data for the form.
        form.save_m2m()

        self.object = new_user

        from_url = "register"
        base_url = reverse(self.get_success_url(), kwargs={'role': 'S'})
        return redirect(base_url + '?uid=%s&from_url=%s' % (uid, from_url))


# 处理教师学生信息更新请求
def update(request, role):
    func = None
    if role == "S":
        func = UpdateStudentView.as_view()
    elif role == "T":
        func = UpdateTeacherView.as_view()

    if func:
        pk = request.session.get("id", "")
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


class UpdateStudentView(UpdateView):
    model = Student
    form_class = StuUpdateForm
    template_name = "user/update.html"

    def get_context_data(self, **kwargs):
        context = super(UpdateStudentView, self).get_context_data(**kwargs)
        context.update(kwargs)
        context["role"] = "S"
        return context

    def get_success_url(self):
        return reverse("course", kwargs={"role": "S"})


class UpdateTeacherView(UpdateView):
    model = Teacher
    form_class = TeaUpdateForm
    template_name = "user/update.html"

    def get_context_data(self, **kwargs):
        context = super(UpdateTeacherView, self).get_context_data(**kwargs)
        context.update(kwargs)
        context["role"] = "T"
        return context

    def get_success_url(self):
        return reverse("course", kwargs={"role": "T"})
