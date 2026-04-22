from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Sneaker


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class SneakerForm(forms.ModelForm):
    sizes_text = forms.CharField(
        label="Размеры",
        help_text="Введите размеры через запятую: 39, 40, 41, 42",
        widget=forms.TextInput(attrs={"placeholder": "39, 40, 41, 42, 43"}),
    )

    class Meta:
        model = Sneaker
        fields = [
            "name",
            "slug",
            "brand",
            "category",
            "price",
            "old_price",
            "colorway",
            "accent_color",
            "short_description",
            "description",
            "sizes_text",
            "model_path",
            "is_featured",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "short_description": forms.Textarea(attrs={"rows": 3}),
            "accent_color": forms.TextInput(attrs={"type": "color"}),
            "model_path": forms.TextInput(attrs={"placeholder": "sneakers/models/scene.gltf"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["sizes_text"].initial = ", ".join(
                str(size) for size in self.instance.sizes
            )

        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.setdefault("class", "form-control")

    def clean_sizes_text(self):
        raw_sizes = self.cleaned_data["sizes_text"]
        sizes = []
        for raw_size in raw_sizes.split(","):
            raw_size = raw_size.strip()
            if not raw_size:
                continue
            try:
                size = int(raw_size)
            except ValueError as exc:
                raise forms.ValidationError("Размеры должны быть числами через запятую.") from exc
            if size < 20 or size > 60:
                raise forms.ValidationError("Размер должен быть в диапазоне от 20 до 60.")
            sizes.append(size)

        if not sizes:
            raise forms.ValidationError("Укажите хотя бы один размер.")

        return sorted(set(sizes))

    def clean_model_path(self):
        return self.cleaned_data["model_path"].replace("\\", "/").strip()

    def save(self, commit=True):
        sneaker = super().save(commit=False)
        sneaker.sizes = self.cleaned_data["sizes_text"]
        if commit:
            sneaker.save()
            self.save_m2m()
        return sneaker
