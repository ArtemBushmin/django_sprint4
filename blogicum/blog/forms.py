from django import forms
from django.contrib.auth.models import User

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ("author",)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
