from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CatalogSneaker:
    name: str
    slug: str
    brand: str
    category: str
    price: Decimal
    old_price: Decimal | None
    colorway: str
    accent_color: str
    short_description: str
    description: str
    sizes: list[int]
    model_path: str
    is_featured: bool = False

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("sneakers:detail", kwargs={"slug": self.slug})


SAMPLE_SNEAKERS = [
    CatalogSneaker(
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
    CatalogSneaker(
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
    CatalogSneaker(
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
