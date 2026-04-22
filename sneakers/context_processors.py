from .models import Favorite, Sneaker

CART_SESSION_KEY = "cart"


def shop_counters(request):
    cart = request.session.get(CART_SESSION_KEY, {})
    cart_count = sum(int(quantity) for quantity in cart.values())
    favorite_count = 0

    if request.user.is_authenticated:
        favorite_count = Favorite.objects.filter(user=request.user).count()

    return {
        "cart_count": cart_count,
        "favorite_count": favorite_count,
    }
