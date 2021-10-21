# usr/bin/env python
# -*- coding:utf-8- -*-
from django import forms
from django.forms import widgets
from .models import Student, Teacher


class StuLoginForm(forms.Form):
    uid = forms.CharField(max_length=10, widget=widgets.TextInput(attrs={'class': 'mdui-textfield-input'}))
    password = forms.CharField(widget=widgets.PasswordInput(attrs={'class': 'mdui-textfield-input'}))


class TeaLoginForm(forms.Form):
    uid = forms.CharField(max_length=10, widget=widgets.TextInput(attrs={'class': 'mdui-textfield-input'}))
    password = forms.CharField(min_length=6, widget=widgets.PasswordInput(attrs={'class': 'mdui-textfield-input'}))


class StuRegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=widgets.PasswordInput(attrs={'class': 'mdui-textfield-input'}))

    class Meta:
        model = Student
        fields = ('grade',
                  'name',
                  'password',
                  'confirm_password',
                  'gender',
                  'birthday',
                  'email',
                  'info')

    def clean(self):
        cleaned_data = super(StuRegisterForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if confirm_password != password:
            self.add_error('confirm_password', 'Password does not match.')

        return cleaned_data


class StuUpdateForm(StuRegisterForm):
    class Meta:
        model = Student
        fields = ('name',
                  'password',
                  'confirm_password',
                  'gender',
                  'birthday',
                  'email',
                  'info')


class TeaRegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=widgets.PasswordInput(attrs={'class': 'mdui-textfield-input'}))

    class Meta:
        model = Teacher
        fields = ('name',
                  'password',
                  'confirm_password',
                  'gender',
                  'birthday',
                  'email',
                  'info')

    def clean(self):
        cleaned_data = super(TeaRegisterForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if confirm_password != password:
            self.add_error('confirm_password', 'Password does not match.')