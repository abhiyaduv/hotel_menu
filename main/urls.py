from django.urls import path
from django.shortcuts import render  # ✅ FIX 1: was missing, caused the NameError
from . import views

urlpatterns = [
    # Public
    path('', views.home),
    path('about/', views.about),
    path('features/', views.features),
    path('contact/', views.contact),

    # Auth
    path('login/', views.login_view),
    path('register/', views.register_view),
    path('logout/', views.logout_view),

    # Dashboard
    path('dashboard/', views.dashboard),
    path('add/', views.add_booking),
    path('delete/<int:id>/', views.delete_booking),

    # Admin
    path('admin-panel/', views.admin_panel),

    # Cart
    path('cart/', views.cart_view),
    path('add-to-cart/<str:name>/<int:price>/', views.add_to_cart),
    path('remove/<int:index>/', views.remove_from_cart),

    # Order                                  ✅ FIX 2: was missing, caused /place-order/ 404
    path('place-order/', views.place_order),
    path('success/', lambda request: render(request, 'success.html')),
]