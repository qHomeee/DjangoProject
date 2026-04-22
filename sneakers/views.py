from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.views.decorators.http import require_POST

from .catalog import SAMPLE_SNEAKERS
from .context_processors import CART_SESSION_KEY
from .forms import RegistrationForm, SneakerForm
from .models import Favorite, Sneaker


def _catalog_queryset():
    sneakers = list(Sneaker.objects.all())
    return sneakers or SAMPLE_SNEAKERS


def home(request):
    sneakers = _catalog_queryset()
    featured = next((item for item in sneakers if item.is_featured), sneakers[0])
    favorite_ids = _favorite_ids(request)
    return render(
        request,
        "sneakers/home.html",
        {
            "sneakers": sneakers,
            "featured": featured,
            "featured_model_url": static(featured.model_path),
            "favorite_ids": favorite_ids,
        },
    )


def sneaker_detail(request, slug):
    sneakers = _catalog_queryset()
    sneaker = next((item for item in sneakers if item.slug == slug), None)
    if sneaker is None:
        from django.http import Http404

        raise Http404("Кроссовки не найдены")

    related = [item for item in sneakers if item.slug != sneaker.slug][:3]
    return render(
        request,
        "sneakers/detail.html",
        {
            "sneaker": sneaker,
            "related": related,
            "model_url": static(sneaker.model_path),
            "favorite_ids": _favorite_ids(request),
        },
    )


def register(request):
    if request.user.is_authenticated:
        return redirect("sneakers:home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Аккаунт создан. Теперь можно пользоваться корзиной и избранным.")
            return redirect("sneakers:home")
    else:
        form = RegistrationForm()

    return render(request, "registration/signup.html", {"form": form})


def _can_manage_sneakers(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _require_manager(user):
    if not _can_manage_sneakers(user):
        raise PermissionDenied("Раздел доступен только администраторам.")


@login_required
def management_dashboard(request):
    _require_manager(request.user)
    sneakers_count = Sneaker.objects.count()
    users_count = User.objects.count()
    favorites_count = Favorite.objects.count()
    latest_sneakers = Sneaker.objects.order_by("-created_at")[:5]
    latest_users = User.objects.order_by("-date_joined")[:5]

    return render(
        request,
        "sneakers/management_dashboard.html",
        {
            "sneakers_count": sneakers_count,
            "users_count": users_count,
            "favorites_count": favorites_count,
            "latest_sneakers": latest_sneakers,
            "latest_users": latest_users,
        },
    )


@login_required
def management_sneaker_list(request):
    _require_manager(request.user)
    query = request.GET.get("q", "").strip()
    brand = request.GET.get("brand", "").strip()
    sneakers = Sneaker.objects.annotate(favorites_total=Count("favorites"))

    if query:
        sneakers = sneakers.filter(
            Q(name__icontains=query)
            | Q(brand__icontains=query)
            | Q(category__icontains=query)
            | Q(colorway__icontains=query)
        )

    if brand:
        sneakers = sneakers.filter(brand=brand)

    brands = Sneaker.objects.order_by("brand").values_list("brand", flat=True).distinct()
    return render(
        request,
        "sneakers/management_sneaker_list.html",
        {
            "sneakers": sneakers,
            "brands": brands,
            "query": query,
            "selected_brand": brand,
        },
    )


@login_required
def sneaker_create(request):
    _require_manager(request.user)

    if request.method == "POST":
        form = SneakerForm(request.POST)
        if form.is_valid():
            sneaker = form.save()
            messages.success(request, "Кроссовки добавлены в каталог.")
            return redirect("sneakers:manage_sneakers")
    else:
        form = SneakerForm(
            initial={
                "category": "Lifestyle",
                "accent_color": "#1495ff",
                "model_path": "sneakers/models/scene.gltf",
            }
        )

    return render(
        request,
        "sneakers/sneaker_form.html",
        {
            "form": form,
            "page_title": "Добавить кроссовки",
            "submit_label": "Добавить в каталог",
        },
    )


@login_required
def sneaker_update(request, pk):
    _require_manager(request.user)
    sneaker = get_object_or_404(Sneaker, pk=pk)

    if request.method == "POST":
        form = SneakerForm(request.POST, instance=sneaker)
        if form.is_valid():
            sneaker = form.save()
            messages.success(request, "Карточка кроссовок обновлена.")
            return redirect("sneakers:manage_sneakers")
    else:
        form = SneakerForm(instance=sneaker)

    return render(
        request,
        "sneakers/sneaker_form.html",
        {
            "form": form,
            "sneaker": sneaker,
            "page_title": f"Редактировать {sneaker.brand} {sneaker.name}",
            "submit_label": "Сохранить изменения",
        },
    )


@login_required
def sneaker_delete(request, pk):
    _require_manager(request.user)
    sneaker = get_object_or_404(Sneaker, pk=pk)

    if request.method == "POST":
        sneaker_name = f"{sneaker.brand} {sneaker.name}"
        sneaker.delete()
        messages.success(request, f"{sneaker_name} удалены из каталога.")
        return redirect("sneakers:manage_sneakers")

    return render(request, "sneakers/sneaker_confirm_delete.html", {"sneaker": sneaker})


def _favorite_ids(request):
    if not request.user.is_authenticated:
        return set()
    return set(
        Favorite.objects.filter(user=request.user).values_list("sneaker_id", flat=True)
    )


def _get_cart(request):
    return request.session.setdefault(CART_SESSION_KEY, {})


def _save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


@login_required
def cart_detail(request):
    cart = _get_cart(request)
    sneaker_ids = [int(sneaker_id) for sneaker_id in cart.keys()]
    preserved_order = Case(
        *[When(id=sneaker_id, then=Value(index)) for index, sneaker_id in enumerate(sneaker_ids)],
        output_field=IntegerField(),
    )
    sneakers = Sneaker.objects.filter(id__in=sneaker_ids).order_by(preserved_order) if sneaker_ids else []
    items = []
    total = 0

    for sneaker in sneakers:
        quantity = int(cart.get(str(sneaker.id), 0))
        subtotal = sneaker.price * quantity
        total += subtotal
        items.append({"sneaker": sneaker, "quantity": quantity, "subtotal": subtotal})

    return render(request, "sneakers/cart.html", {"items": items, "total": total})


@login_required
@require_POST
def cart_add(request, pk):
    sneaker = get_object_or_404(Sneaker, pk=pk)
    cart = _get_cart(request)
    sneaker_key = str(sneaker.id)
    cart[sneaker_key] = int(cart.get(sneaker_key, 0)) + 1
    _save_cart(request, cart)
    messages.success(request, f"{sneaker.brand} {sneaker.name} добавлены в корзину.")
    return redirect(request.POST.get("next") or sneaker.get_absolute_url())


@login_required
@require_POST
def cart_remove(request, pk):
    sneaker = get_object_or_404(Sneaker, pk=pk)
    cart = _get_cart(request)
    cart.pop(str(sneaker.id), None)
    _save_cart(request, cart)
    messages.success(request, f"{sneaker.brand} {sneaker.name} удалены из корзины.")
    return redirect("sneakers:cart")


@login_required
def favorites_detail(request):
    favorites = (
        Favorite.objects.filter(user=request.user)
        .select_related("sneaker")
    )
    return render(request, "sneakers/favorites.html", {"favorites": favorites})


@login_required
@require_POST
def favorite_toggle(request, pk):
    sneaker = get_object_or_404(Sneaker, pk=pk)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        sneaker=sneaker,
    )
    if created:
        messages.success(request, f"{sneaker.brand} {sneaker.name} добавлены в избранное.")
    else:
        favorite.delete()
        messages.success(request, f"{sneaker.brand} {sneaker.name} удалены из избранного.")
    return redirect(request.POST.get("next") or sneaker.get_absolute_url())
