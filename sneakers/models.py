from django.db import models
from django.conf import settings
from django.urls import reverse


class Sneaker(models.Model):
    name = models.CharField("Название", max_length=120)
    slug = models.SlugField("URL", max_length=140, unique=True)
    brand = models.CharField("Бренд", max_length=80)
    category = models.CharField("Категория", max_length=80, default="Lifestyle")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        "Старая цена",
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    colorway = models.CharField("Расцветка", max_length=120)
    accent_color = models.CharField("Акцентный цвет", max_length=7, default="#0ea5e9")
    short_description = models.CharField("Краткое описание", max_length=220)
    description = models.TextField("Описание")
    sizes = models.JSONField("Размеры", default=list)
    model_path = models.CharField(
        "Путь к 3D модели в static",
        max_length=220,
        default="sneakers/models/scene.gltf",
        help_text="Например: sneakers/models/scene.gltf",
    )
    is_featured = models.BooleanField("На главной", default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        ordering = ["brand", "name"]
        verbose_name = "Кроссовок"
        verbose_name_plural = "Кроссовки"

    def __str__(self):
        return f"{self.brand} {self.name}"

    def get_absolute_url(self):
        return reverse("sneakers:detail", kwargs={"slug": self.slug})


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_sneakers",
        verbose_name="Пользователь",
    )
    sneaker = models.ForeignKey(
        Sneaker,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Кроссовки",
    )
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "sneaker"],
                name="unique_user_favorite_sneaker",
            )
        ]
        ordering = ["-created_at"]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

    def __str__(self):
        return f"{self.user} - {self.sneaker}"
