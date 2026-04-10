from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking


# ─── PUBLIC PAGES ─────────────────────────────────────────────
def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def features(request):
    return render(request, 'features.html')

def contact(request):
    return render(request, 'contact.html')


# ─── AUTH ──────────────────────────────────────────────────────
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect('/register/')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('/register/')

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully!")
        return redirect('/login/')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('/dashboard/')
        else:
            # FIX: was silently failing — now shows an error
            messages.error(request, "Invalid username or password.")
            return redirect('/login/')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/')


# ─── USER DASHBOARD ────────────────────────────────────────────
@login_required
def dashboard(request):
    data = Booking.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'data': data})


@login_required
def add_booking(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()

        # FIX: prevent saving empty bookings
        if title and description:
            Booking.objects.create(
                user=request.user,
                title=title,
                description=description
            )
        else:
            messages.error(request, "Title and description cannot be empty.")

    return redirect('/dashboard/')


@login_required
def delete_booking(request, id):
    # FIX: use get_object_or_404 to avoid crash on invalid ID
    booking = get_object_or_404(Booking, id=id, user=request.user)
    booking.delete()
    return redirect('/dashboard/')


# ─── ADMIN PANEL ───────────────────────────────────────────────
def admin_panel(request):
    if not request.user.is_superuser:
        return redirect('/')

    users = User.objects.all()
    data = Booking.objects.all()

    return render(request, 'admin_panel.html', {
        'users': users,
        'data': data
    })


# ─── CART ──────────────────────────────────────────────────────
def add_to_cart(request, name, price):
    cart = request.session.get('cart', [])

    cart.append({
        'name': name,
        'price': float(price)
    })

    request.session['cart'] = cart
    return redirect('/cart/')


def cart_view(request):
    cart = request.session.get('cart', [])
    total = sum(item['price'] for item in cart)

    return render(request, 'cart.html', {
        'cart': cart,
        'total': total
    })


def remove_from_cart(request, index):
    cart = request.session.get('cart', [])

    # FIX: bounds check before popping
    if 0 <= index < len(cart):
        cart.pop(index)
        request.session['cart'] = cart

    return redirect('/cart/')


# ─── ORDER ─────────────────────────────────────────────────────
def place_order(request):
    # FIX: this view was missing entirely — caused /place-order/ 404
    request.session['cart'] = []  # clear cart
    return redirect('/success/')