from django.urls import path

from . import views

app_name = "sneakers"

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/signup/", views.register, name="signup"),
    path("cart/", views.cart_detail, name="cart"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path("favorites/", views.favorites_detail, name="favorites"),
    path("favorites/toggle/<int:pk>/", views.favorite_toggle, name="favorite_toggle"),
    path("sneakers/add/", views.sneaker_create, name="create"),
    path("sneakers/<slug:slug>/", views.sneaker_detail, name="detail"),
]
