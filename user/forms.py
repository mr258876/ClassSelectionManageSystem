# usr/bin/env python
# -*- coding:utf-8- -*-
from django import forms
from django.forms import widgets
from .models import User
from course.models import Student, Teacher

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model


# 用户登陆表单
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=widgets.TextInput(
        attrs={'class': 'mdui-textfield-input', 'pattern': '(^[0138])[0-9]{1,7}'}))
    password = forms.CharField(widget=widgets.PasswordInput(
        attrs={'class': 'mdui-textfield-input'}))
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'password')


# 用户注册表单
class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=widgets.TextInput(
        attrs={'class': 'mdui-textfield-input', 'pattern': '(^[0138])[0-9]{1,7}', 'maxlength': 8}))
    password1 = forms.CharField(max_length=16, widget=widgets.PasswordInput(
        attrs={'class': 'mdui-textfield-input', 'pattern': '^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,16}$', 'maxlength': 16}))
    password2 = forms.CharField(max_length=16, widget=widgets.PasswordInput(
        attrs={'class': 'mdui-textfield-input', 'pattern': '^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,16}$', 'maxlength': 16}))
    email = forms.CharField(widget=widgets.EmailInput(
        attrs={'class': 'mdui-textfield-input'}))
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'email')

    def username_clean(self):  
        username = self.cleaned_data['username'].lower()
        new = User.objects.filter(username = username)  
        if new.count():  
            raise ValidationError("User Already Exist")  
        return username  
  
    # def email_clean(self):  
    #     email = self.cleaned_data['email'].lower()
    #     new = User.objects.filter(email=email)  
    #     if new.count():  
    #         raise ValidationError("Email Already Exist")  
    #     return email  
  
    def clean_password(self):  
        password1 = self.cleaned_data['password1']  
        password2 = self.cleaned_data['password2']  
  
        if password1 and password2 and password1 != password2:  
            raise ValidationError("Password don't match")  
        return password1
  
    def save(self, commit = True):  
        user = User.objects.create_user(  
            self.cleaned_data['username'],
            self.cleaned_data['password1'],
            self.cleaned_data['email'],
        )  
        return user  


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
        cleaned_data = super().clean()
        password1 = self.cleaned_data['password1']  
        password2 = self.cleaned_data['password2']  
  
        if password1 and password2 and password1 != password2:  
            raise ValidationError("Password don't match")
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
