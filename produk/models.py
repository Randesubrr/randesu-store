from django.db import models
from users.models import User


class Produk(models.Model):
    nama = models.CharField(max_length=100)
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    stok = models.PositiveIntegerField()
    kategori = models.CharField(max_length=50)
    gambar = models.ImageField(upload_to='produk/', null=True, blank=True)  # <--- Tambahan

    def __str__(self):
        return self.nama

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart milik {self.user.username}"

    def total_harga(self):
        return sum(item.total_harga() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.produk.nama}"

    def total_harga(self):
        return self.produk.harga * self.quantity


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    bintang = models.IntegerField(choices=[(i, i) for i in range(1, 6)])

    class Meta:
        unique_together = ('user', 'produk')  # biar user hanya bisa rating sekali