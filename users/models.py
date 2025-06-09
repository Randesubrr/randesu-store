from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('petugas', 'Petugas'),
        ('pembeli', 'Pembeli'),

    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_admin = models.BooleanField(default=False)
    is_pelanggan = models.BooleanField(default=True)