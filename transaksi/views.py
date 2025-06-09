from django.contrib import messages
from produk.models import Produk, Cart, CartItem
from .models import Transaksi, TransaksiItem
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
import csv
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required

# ===============================
# Proses checkout dari keranjang
# ===============================
@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    items = cart.items.all()

    if not items:
        messages.warning(request, "Keranjang kamu kosong.")
        return redirect('view_cart')

    transaksi = Transaksi.objects.create(user=request.user, total_harga=0)
    total = 0

    for item in items:
        produk = item.produk

        if produk.stok < item.quantity:
            messages.error(request, f"Stok {produk.nama} tidak cukup.")
            transaksi.delete()
            return redirect('view_cart')

        produk.stok -= item.quantity
        produk.save()

        # Simpan detail per-produk dalam transaksi
        TransaksiItem.objects.create(
            transaksi=transaksi,
            produk=produk,
            quantity=item.quantity,
            harga_saat_beli=produk.harga
        )

        total += produk.harga * item.quantity

    transaksi.total_harga = total
    transaksi.save()

    # Bersihkan keranjang setelah checkout
    items.delete()

    messages.success(request, "Pembelian berhasil!")
    return redirect('transaksi:histori_transaksi')


# ============================
# Riwayat transaksi pengguna
# ============================
@login_required
def histori_transaksi(request):
    transaksis = Transaksi.objects.filter(user=request.user).order_by('-tanggal')
    return render(request, 'histori.html', {'transaksis': transaksis})


# ==================================================
# Fungsi utilitas (checkout otomatis tanpa tampilan)
# ==================================================
def do_checkout(user):
    cart = Cart.objects.get(user=user)
    items = cart.items.all()
    if not items:
        return None, "Keranjang kosong"

    transaksi = Transaksi.objects.create(user=user, total_harga=0)
    total = 0

    for item in items:
        produk = item.produk
        if produk.stok < item.quantity:
            transaksi.delete()
            return None, f"Stok {produk.nama} tidak cukup."

        produk.stok -= item.quantity
        produk.save()

        TransaksiItem.objects.create(
            transaksi=transaksi,
            produk=produk,
            quantity=item.quantity,
            harga_saat_beli=produk.harga
        )
        total += produk.harga * item.quantity

    transaksi.total_harga = total
    transaksi.save()
    items.delete()
    return transaksi, None


# =======================================
# Beli + langsung checkout tanpa ke cart
# =======================================
@login_required
def add_to_cart_and_checkout(request, produk_id):
    produk = get_object_or_404(Produk, id=produk_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, produk=produk)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    transaksi, error = do_checkout(request.user)
    if error:
        messages.error(request, error)
        return redirect('view_cart')
    messages.success(request, "Pembelian berhasil!")
    return redirect('transaksi:histori_transaksi')


# ===============================
# Hapus semua histori transaksi
# ===============================
@login_required
def clear_history(request):
    if request.method == 'POST':
        Transaksi.objects.filter(user=request.user).delete()
    return redirect('transaksi:histori_transaksi')


# ===================================
# Cetak PDF struk untuk 1 transaksi
# ===================================
@login_required
def cetak_transaksi_struk(request, id_transaksi):
    try:
        transaksi = Transaksi.objects.get(id=id_transaksi)
    except Transaksi.DoesNotExist:
        return HttpResponse('Transaksi tidak ditemukan', status=404)

    template_path = 'struk.html'
    context = {'transaksi': transaksi}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="struk.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Gagal membuat PDF', status=500)
    return response


# ================================
# Ekspor data transaksi ke CSV
# ================================
@user_passes_test(lambda u: u.is_superuser)
def export_transaksi_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transaksi.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'User', 'Tanggal', 'Total Harga'])

    transaksi_list = Transaksi.objects.all()
    for t in transaksi_list:
        writer.writerow([t.id, t.user.username, t.tanggal, t.total_harga])

    return response


# ======================================================
# Admin mengubah status transaksi secara manual (POST)
# ======================================================
@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def ubah_status_transaksi(request, id):
    transaksi = get_object_or_404(Transaksi, id=id)
    if request.method == 'POST':
        status_baru = request.POST.get('status')
        transaksi.status = status_baru
        transaksi.save()
        messages.success(request, 'Status transaksi berhasil diubah.')
    return redirect('dashboard')


# =====================================================
# Bayar dari keranjang (penuh atau hanya 1 item saja)
# =====================================================
@login_required
def bayar_dari_cart(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)

    # ✅ Bayar hanya satu item
    item_id = request.POST.get('item_id')
    if item_id:
        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        transaksi = Transaksi.objects.create(
            user=request.user,
            total_harga=item.quantity * item.produk.harga,
            status='belum dibayar',
            cart=cart
        )

        TransaksiItem.objects.create(
            transaksi=transaksi,
            produk=item.produk,
            quantity=item.quantity,
            harga_saat_beli=item.produk.harga
        )

        item.delete()

        return render(request, 'bayar.html', {'transaksi': transaksi})

    # 🛒 Bayar seluruh isi keranjang
    if not cart.items.exists():
        messages.warning(request, "Keranjang kosong.")
        return redirect('view_cart')

    transaksi = Transaksi.objects.filter(
        user=request.user,
        cart=cart,
        status__in=['belum dibayar', 'pending']
    ).first()

    if not transaksi:
        transaksi = Transaksi.objects.create(
            user=request.user,
            total_harga=cart.total_harga(),
            status='belum dibayar',
            cart=cart,
        )

        for item in cart.items.all():
            TransaksiItem.objects.create(
                transaksi=transaksi,
                produk=item.produk,
                quantity=item.quantity,
                harga_saat_beli=item.produk.harga
            )

    return render(request, 'bayar.html', {'transaksi': transaksi})


# =====================================================
# Proses pembayaran (parsial / penuh)
# Update status transaksi otomatis
# =====================================================
@login_required
@csrf_exempt
def proses_pembayaran(request, transaksi_id):
    transaksi = get_object_or_404(Transaksi, id=transaksi_id, user=request.user)

    if request.method == 'POST':
        jumlah_bayar = int(request.POST.get('jumlah_bayar', 0))
        transaksi.jumlah_terbayar += jumlah_bayar

        if transaksi.jumlah_terbayar >= transaksi.total_harga:
            transaksi.status = 'sudah dibayar'
            # Kurangi stok dan hapus cart
            cart = transaksi.cart
            if cart:
                for item in cart.items.all():
                    produk = item.produk
                    produk.stok -= item.quantity
                    produk.save()
                cart.items.all().delete()
        elif transaksi.jumlah_terbayar > 0:
            transaksi.status = 'pending'
        else:
            transaksi.status = 'belum dibayar'

        transaksi.save()
        messages.success(request, f"Status pembayaran: {transaksi.status}")
        return redirect('transaksi:histori_transaksi')

    return HttpResponse("Metode tidak diizinkan", status=405)


# ===================================
# Beli langsung tanpa keranjang
# ===================================
@login_required
def beli_langsung(request, produk_id):
    produk = get_object_or_404(Produk, id=produk_id)

    if produk.stok < 1:
        messages.error(request, "Stok tidak mencukupi.")
        return redirect('daftar_produk')

    transaksi = Transaksi.objects.create(
        user=request.user,
        total_harga=produk.harga,
        jumlah_terbayar=0,
        status='belum dibayar',
        cart=None
    )

    TransaksiItem.objects.create(
        transaksi=transaksi,
        produk=produk,
        quantity=1,
        harga_saat_beli=produk.harga
    )

    return redirect('transaksi:halaman_bayar', transaksi_id=transaksi.id)


# ===============================
# Halaman pembayaran transaksi
# ===============================
@login_required
def halaman_bayar(request, transaksi_id):
    transaksi = get_object_or_404(Transaksi, id=transaksi_id, user=request.user)
    return render(request, 'bayar.html', {'transaksi': transaksi})