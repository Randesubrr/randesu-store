from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Produk
from .models import Rating

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ProdukForm(forms.ModelForm):
    class Meta:
        model = Produk
        fields = ['nama', 'harga', 'stok', 'kategori', 'gambar']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['bintang']