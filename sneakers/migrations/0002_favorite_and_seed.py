from decimal import Decimal

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def seed_sneakers(apps, schema_editor):
    Sneaker = apps.get_model("sneakers", "Sneaker")
    if Sneaker.objects.exists():
        return

    Sneaker.objects.bulk_create(
        [
            Sneaker(
                name="Air TN Hyper Blue",
                slug="air-tn-hyper-blue",
                brand="Nike",
                category="Running Archive",
                price=Decimal("18990.00"),
                old_price=Decimal("21990.00"),
                colorway="Hyper Blue / Black / White",
                accent_color="#1495ff",
                short_description="Культовый силуэт с агрессивными линиями и мягкой амортизацией.",
                description=(
                    "Пара для витрины, прогулок и коллекции. Верх сочетает сетку и плотные "
                    "накладки, а 3D-просмотр помогает оценить форму, профиль подошвы и детали."
                ),
                sizes=[39, 40, 41, 42, 43, 44, 45],
                model_path="sneakers/models/scene.gltf",
                is_featured=True,
            ),
            Sneaker(
                name="Wave Runner Silver",
                slug="wave-runner-silver",
                brand="Adidas",
                category="Streetwear",
                price=Decimal("16490.00"),
                old_price=None,
                colorway="Silver / Graphite / Solar Red",
                accent_color="#ef4444",
                short_description="Объёмный ретро-беговой профиль для городских образов.",
                description=(
                    "Модель рассчитана на плотную ежедневную носку: цепкая подошва, мягкая "
                    "посадка и выразительная многослойная конструкция."
                ),
                sizes=[38, 39, 40, 41, 42, 43],
                model_path="sneakers/models/scene.gltf",
            ),
            Sneaker(
                name="Gel Pulse Mint",
                slug="gel-pulse-mint",
                brand="ASICS",
                category="Performance",
                price=Decimal("13990.00"),
                old_price=Decimal("15490.00"),
                colorway="Mint / Cream / Carbon",
                accent_color="#14b8a6",
                short_description="Лёгкая тренировочная пара с чистым технологичным силуэтом.",
                description=(
                    "Подходит для тренировок и активного города. 3D-модель на странице товара "
                    "помогает рассмотреть объём подошвы, носок и боковые панели."
                ),
                sizes=[40, 41, 42, 43, 44, 45, 46],
                model_path="sneakers/models/scene.gltf",
            ),
        ]
    )


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("sneakers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Favorite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")),
                (
                    "sneaker",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorites",
                        to="sneakers.sneaker",
                        verbose_name="Кроссовки",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorite_sneakers",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Избранное",
                "verbose_name_plural": "Избранное",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="favorite",
            constraint=models.UniqueConstraint(
                fields=("user", "sneaker"),
                name="unique_user_favorite_sneaker",
            ),
        ),
        migrations.RunPython(seed_sneakers, migrations.RunPython.noop),
    ]
