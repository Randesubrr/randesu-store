from django.db import models
from users.models import User
from produk.models import Produk

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('dibayar', 'Dibayar'),
    ('dikirim', 'Dikirim'),
    ('selesai', 'Selesai'),
]

class Transaksi(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_harga = models.DecimalField(max_digits=10, decimal_places=2)
    tanggal = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cart = models.ForeignKey('produk.Cart', on_delete=models.SET_NULL, null=True, blank=True)  # Tambahan
    jumlah_terbayar = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Tambahan

class TransaksiItem(models.Model):
    transaksi = models.ForeignKey(Transaksi, on_delete=models.CASCADE, related_name='items')
    produk = models.ForeignKey(Produk, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    harga_saat_beli = models.DecimalField(max_digits=10, decimal_places=2)
