from django import forms
from django.forms import widgets
from user.models import User

from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from django.conf import settings


###############################################################
# APIs

# 用户注册表单
class AddUserForm(UserCreationForm):
    username = forms.CharField(widget=widgets.TextInput(
        attrs={'class': 'mdui-textfield-input', 'pattern': settings.USER_NAME_PATTERN, 'maxlength': 8}))
    name = forms.CharField(widget=widgets.TextInput(
        attrs={'class': 'mdui-textfield-input'}), required=False)
    password1 = forms.CharField(max_length=16, widget=widgets.PasswordInput(
        attrs={'class': 'mdui-textfield-input', 'pattern': settings.USER_PSWD_PATTERN, 'maxlength': 16}))
    password2 = forms.CharField(max_length=16, widget=widgets.PasswordInput(
        attrs={'class': 'mdui-textfield-input', 'pattern': settings.USER_PSWD_PATTERN, 'maxlength': 16}))
    email = forms.CharField(widget=widgets.EmailInput(
        attrs={'class': 'mdui-textfield-input'}))
    user_role = forms.CharField(widget=widgets.TextInput(
        attrs={'class': 'mdui-textfield-input'}))
    
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('email', 'user_role', 'name',)

    def clean_username(self):  
        username = self.cleaned_data['username'].lower()
        new = User.objects.filter(uid = username)  
        if new.count():  
            raise ValidationError("User Already Exist")  
        return username
  
    def save(self, commit = True):  
        user = User.objects.create_user(  
            self.cleaned_data['username'],
            self.cleaned_data['password1'],
            self.cleaned_data['email'],
            self.cleaned_data['user_role'],
        )  
        return user
