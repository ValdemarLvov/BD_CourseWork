from django import forms
from django.contrib.auth.models import User

from .models import Video


class VideoForm(forms.ModelForm):

    class Meta:
        model = Video
        fields = ['title', 'videofile']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']
