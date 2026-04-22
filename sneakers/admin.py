from django.contrib import admin

from .models import Favorite, Sneaker


@admin.register(Sneaker)
class SneakerAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "price", "has_image", "has_model_file", "is_featured")
    list_filter = ("brand", "category", "is_featured")
    prepopulated_fields = {"slug": ("brand", "name")}
    search_fields = ("name", "brand", "colorway")

    @admin.display(boolean=True, description="Картинка")
    def has_image(self, obj):
        return bool(obj.image)

    @admin.display(boolean=True, description="3D файл")
    def has_model_file(self, obj):
        return bool(obj.model_file)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "sneaker", "created_at")
    search_fields = ("user__username", "sneaker__name", "sneaker__brand")
