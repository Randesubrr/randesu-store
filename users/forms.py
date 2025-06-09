# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User  # pastikan ini import model kamu yang benar

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')  # tambahkan field lain kalau perlu
