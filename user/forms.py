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
        import datetime

        model = Student
        fields = ('grade',
                  'name',
                  'password',
                  'confirm_password',
                  'gender',
                  'birthday',
                  'email'
                  )
        widgets = {'grade': widgets.TextInput(attrs={'class': 'mdui-textfield-input'}),
                  'name': widgets.TextInput(attrs={'class': 'mdui-textfield-input'}),
                  'password': widgets.PasswordInput(attrs={'class': 'mdui-textfield-input'}),
                  'confirm_password': widgets.PasswordInput(attrs={'class': 'mdui-textfield-input'}),
                  'gender': widgets.Select(attrs={'class': 'mdui-select mdui-textfield-input'}),
                  'birthday': widgets.DateInput(attrs={'class': 'mdui-textfield-input', 'type': 'date'}),
                  'email': widgets.EmailInput(attrs={'class': 'mdui-textfield-input'})
                  }

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
                  )


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
                  )

    def clean(self):
        cleaned_data = super(TeaRegisterForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if confirm_password != password:
            self.add_error('confirm_password', 'Password does not match.')