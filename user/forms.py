# usr/bin/env python
# -*- coding:utf-8- -*-
from django import forms
from django.forms import widgets
from django.contrib.auth.forms import AuthenticationForm
from .models import Student, Teacher, User


# 用户登陆表单
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=widgets.TextInput(
        attrs={'class': 'mdui-textfield-input', 'pattern': '(^[0138])[0-9]{1,7}'}))
    password = forms.CharField(widget=widgets.PasswordInput(
        attrs={'class': 'mdui-textfield-input'}))


# 用户注册表单
class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(max_length=16, widget=widgets.PasswordInput(
        attrs={'class': 'mdui-textfield-input', 'pattern': '^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,16}$', 'maxlength': 16}))
    confirm_password = forms.CharField(max_length=16, widget=widgets.PasswordInput(
        attrs={'class': 'mdui-textfield-input', 'pattern': '^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,16}$', 'maxlength': 16}))

    class Meta:
        model = User
        fields = ('uid',
                  'password',
                  'confirm_password',
                  'email',
                  )
        widgets = {'uid': widgets.TextInput(attrs={'class': 'mdui-textfield-input', 'pattern': '(^[0138])[0-9]{1,7}'}),
                   'password': widgets.PasswordInput(attrs={'class': 'mdui-textfield-input', 'pattern': '^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,16}$'}),
                   'confirm_password': widgets.PasswordInput(attrs={'class': 'mdui-textfield-input'}),
                   'email': widgets.EmailInput(attrs={'class': 'mdui-textfield-input'})
                   }

    def clean(self):
        cleaned_data = super(UserRegisterForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if confirm_password != password:
            self.add_error('confirm_password', 'Password does not match.')

        return cleaned_data


# 用户信息更新表单
class UserUpdateForm(forms.ModelForm):
    password = forms.CharField(max_length=16, widget=widgets.PasswordInput(
        attrs={'class': 'mdui-textfield-input', 'pattern': '^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,16}$'}))
    confirm_password = forms.CharField(max_length=40, widget=widgets.PasswordInput(
        attrs={'class': 'mdui-textfield-input', 'pattern': '^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,16}$'}))

    class Meta:
        model = User
        fields = ('password',
                  'confirm_password',
                  'email',
                  )
        widgets = {'password': widgets.PasswordInput(attrs={'class': 'mdui-textfield-input'}),
                   'confirm_password': widgets.PasswordInput(attrs={'class': 'mdui-textfield-input'}),
                   'email': widgets.EmailInput(attrs={'class': 'mdui-textfield-input'})
                   }

    def clean(self):
        cleaned_data = super(UserRegisterForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if confirm_password != password:
            self.add_error('confirm_password', 'Password does not match.')

        return cleaned_data


# 学生个人信息更新
class StuUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('name',
                  'gender',
                  'birthday'
                  )
        widgets = {'name': widgets.TextInput(attrs={'class': 'mdui-textfield-input'}),
                   'gender': widgets.Select(attrs={'class': 'mdui-select mdui-textfield-input'}),
                   'birthday': widgets.DateInput(attrs={'class': 'mdui-textfield-input', 'type': 'date'})
                   }


# 教师个人信息更新
class TeaUpdateForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ('name',
                  'gender',
                  'birthday',
                  'info',
                  )
        widgets = {'name': widgets.TextInput(attrs={'class': 'mdui-textfield-input'}),
                   'gender': widgets.Select(attrs={'class': 'mdui-select mdui-textfield-input'}),
                   'birthday': widgets.DateInput(attrs={'class': 'mdui-textfield-input', 'type': 'date'}),
                   'info': widgets.Textarea(attrs={'class': 'mdui-textfield-input'}),
                   }
