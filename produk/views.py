# Mengimpor model Produk
from .models import Produk 
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegisterForm, ProdukForm, RatingForm
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from users.forms import CustomUserCreationForm
from .models import Cart, CartItem, Rating
from transaksi.views import checkout
from django.utils.timezone import now
from django.db.models import Sum, Avg, Count
from django.core.paginator import Paginator
from transaksi.models import Transaksi
from django.contrib.auth.decorators import user_passes_test

# ======== HALAMAN UMUM ========

# Landing page - Menampilkan 3 produk terbaru sebagai highlight di halaman utama
def landing_page(request):
    produk_terbaru = Produk.objects.all()[:3]  # Ambil 3 produk pertama
    return render(request, 'landing.html', {'produk_terbaru': produk_terbaru})

# ======== KATALOG PRODUK ========

# Halaman katalog - Menampilkan semua produk, bisa disaring pakai search query
@login_required
def daftar_produk(request):
    query = request.GET.get('q')
    if query:
        semua_produk = Produk.objects.filter(nama__icontains=query)
    else:
        semua_produk = Produk.objects.all()

    # Anotasi rating rata-rata dan jumlah rating per produk
    semua_produk = semua_produk.annotate(
        rata_rating=Avg('rating__bintang'),
        jumlah_rating=Count('rating')
    )

    paginator = Paginator(semua_produk, 6)  # Paginasi, 6 produk per halaman
    page_number = request.GET.get('page') or 1  
    page_obj = paginator.get_page(page_number)

    return render(request, 'daftar_produk.html', {
        'produk_list': page_obj.object_list,
        'page_obj': page_obj,
    })

# Detail produk - Menampilkan info lengkap dari 1 produk tertentu
def detail_produk(request, produk_id):
    produk = get_object_or_404(Produk, id=produk_id)
    return render(request, 'detail_produk.html', {'produk': produk})

# ======== AUTENTIKASI PENGGUNA ========

# Register - Halaman untuk user baru mendaftar akun
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Akun berhasil dibuat. Silakan login!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# ======== KERANJANG BELANJA ========

# Tambah produk ke cart
def add_to_cart(request, produk_id):
    produk = get_object_or_404(Produk, id=produk_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, produk=produk)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('view_cart')

# Tambah ke cart lalu langsung checkout
def add_to_cart_and_history(request, produk_id):
    produk = get_object_or_404(Produk, id=produk_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, produk=produk)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return checkout(request)

# Lihat isi cart
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    return render(request, 'cart.html', {'items': items, 'cart': cart})

# Hapus 1 item dari cart
def hapus_item_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    if item.cart.user == request.user:
        item.delete()
    return redirect('view_cart')

# Kurangi jumlah item di cart
def kurangi_item_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    if item.cart.user == request.user:
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    return redirect('view_cart')

# Tambah jumlah item di cart
def tambah_item_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    if item.cart.user == request.user:
        item.quantity += 1
        item.save()
    return redirect('view_cart')

# ======== DASHBOARD ADMIN ========

# Cek apakah user adalah admin
def is_admin(user):
    return user.is_superuser

# Dashboard admin - Tampilkan statistik pengguna, produk, transaksi, dll
@login_required
@user_passes_test(is_admin)
def dashboard(request):
    User = get_user_model()
    today = now().date()

    transaksi_list = Transaksi.objects.all().order_by('-tanggal')

    context = {
        'total_users': User.objects.count(),
        'total_produk': Produk.objects.count(),
        'total_transaksi': Transaksi.objects.count(),
        'transaksi_hari_ini': Transaksi.objects.filter(tanggal__date=today).count(),
        'total_pendapatan': Transaksi.objects.aggregate(Sum('total_harga'))['total_harga__sum'] or 0,
        'produk_stok_tipis': Produk.objects.filter(stok__lt=5),
        'transaksi_list': transaksi_list,
    }

    return render(request, 'dashboard.html', context)

# Hapus produk - Hanya admin yang bisa
@user_passes_test(lambda u: u.is_superuser)
def hapus_produk(request, id):
    produk = get_object_or_404(Produk, id=id)
    produk.delete()
    return redirect('daftar_produk')

# Edit produk - Hanya admin yang bisa
@login_required
def edit_produk(request, id):
    if not request.user.is_superuser:
        return redirect('daftar_produk')

    produk = get_object_or_404(Produk, id=id)
    if request.method == 'POST':
        form = ProdukForm(request.POST, request.FILES, instance=produk)
        if form.is_valid():
            form.save()
            return redirect('detail_produk', produk_id=produk.id)
    else:
        form = ProdukForm(instance=produk)

    return render(request, 'edit_produk.html', {'form': form, 'produk': produk})

# ======== FITUR RATING PRODUK ========

# Beri atau update rating untuk produk
@login_required
def beri_rating(request, produk_id):
    produk = get_object_or_404(Produk, id=produk_id)
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating, created = Rating.objects.update_or_create(
                user=request.user,
                produk=produk,
                defaults={'bintang': form.cleaned_data['bintang']}
            )
            return redirect('daftar_produk')
