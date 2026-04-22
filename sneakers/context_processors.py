from .models import CartItem, Favorite


def shop_counters(request):
    cart_count = 0
    favorite_count = 0

    if request.user.is_authenticated:
        cart_count = sum(
            CartItem.objects.filter(user=request.user).values_list("quantity", flat=True)
        )
        favorite_count = Favorite.objects.filter(user=request.user).count()

    return {
        "cart_count": cart_count,
        "favorite_count": favorite_count,
    }
