# produk/urls.py

from django.urls import path
from . import views
from .views import register


urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('daftar/', views.daftar_produk, name='daftar_produk'),
    path('<int:produk_id>/', views.detail_produk, name='detail_produk'),  # <-- Tambahkan ini
    path('register/', register, name='register'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:produk_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/hapus/<int:item_id>/', views.hapus_item_cart, name='hapus_item'),
    path('cart/kurangi/<int:item_id>/', views.kurangi_item_cart, name='kurangi_item'),
    path('add-to-cart-history/<int:produk_id>/', views.add_to_cart_and_history, name='add_to_cart_and_history'),
    path('cart/tambah/<int:item_id>/', views.tambah_item_cart, name='tambah_item'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('produk/hapus/<int:id>/', views.hapus_produk, name='hapus_produk'),
    path('produk/edit/<int:id>/', views.edit_produk, name='edit_produk'),
    path('produk/<int:produk_id>/rating/', views.beri_rating, name='beri_rating'),
]