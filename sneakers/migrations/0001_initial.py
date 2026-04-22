# Generated for the sneaker store demo.
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Sneaker",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, verbose_name="Название")),
                ("slug", models.SlugField(max_length=140, unique=True, verbose_name="URL")),
                ("brand", models.CharField(max_length=80, verbose_name="Бренд")),
                ("category", models.CharField(default="Lifestyle", max_length=80, verbose_name="Категория")),
                ("price", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Цена")),
                ("old_price", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name="Старая цена")),
                ("colorway", models.CharField(max_length=120, verbose_name="Расцветка")),
                ("accent_color", models.CharField(default="#0ea5e9", max_length=7, verbose_name="Акцентный цвет")),
                ("short_description", models.CharField(max_length=220, verbose_name="Краткое описание")),
                ("description", models.TextField(verbose_name="Описание")),
                ("sizes", models.JSONField(default=list, verbose_name="Размеры")),
                ("model_path", models.CharField(default="sneakers/models/scene.gltf", help_text="Например: sneakers/models/scene.gltf", max_length=220, verbose_name="Путь к 3D модели в static")),
                ("is_featured", models.BooleanField(default=False, verbose_name="На главной")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
            ],
            options={
                "verbose_name": "Кроссовок",
                "verbose_name_plural": "Кроссовки",
                "ordering": ["brand", "name"],
            },
        ),
    ]
