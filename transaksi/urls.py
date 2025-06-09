from django.urls import path
from . import views
from transaksi.views import cetak_transaksi_struk
from .views import export_transaksi_csv
app_name = 'transaksi'


urlpatterns = [
    path('', views.histori_transaksi, name='histori_transaksi'),
    path('checkout/', views.checkout, name='checkout'),
    path('histori/', views.histori_transaksi, name='histori_transaksi'),
    path('clear-history/', views.clear_history, name='clear_history'),
    path('cetak_transaksi_struk/<int:id_transaksi>/', views.cetak_transaksi_struk, name='cetak_transaksi_struk'),
    path('export-transaksi/', export_transaksi_csv, name='export_transaksi'),
    path('ubah-status/<int:id>/', views.ubah_status_transaksi, name='ubah_status_transaksi'),
    path('bayar-dari-cart/<int:cart_id>/', views.bayar_dari_cart, name='bayar_dari_cart'),
    path('proses-pembayaran/<int:transaksi_id>/', views.proses_pembayaran, name='proses_pembayaran'),
    path('beli-langsung/<int:produk_id>/', views.beli_langsung, name='beli_langsung'),
    path('bayar/<int:transaksi_id>/', views.halaman_bayar, name='halaman_bayar'),
]