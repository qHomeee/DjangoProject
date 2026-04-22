from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import CartItem, Favorite, Sneaker


class SneakerPageTests(TestCase):
    def test_home_page_renders_catalog(self):
        response = self.client.get(reverse("sneakers:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "3D Sneaker Store")
        self.assertContains(response, "Air TN Hyper Blue")

    def test_detail_page_sets_model_path(self):
        response = self.client.get(
            reverse("sneakers:detail", kwargs={"slug": "air-tn-hyper-blue"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "window.SNEAKER_MODEL")
        self.assertContains(response, "sneakers/models/scene.gltf")


class SneakerCreateTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.staff_user = user_model.objects.create_user(
            username="manager",
            password="pass12345",
            is_staff=True,
        )
        self.regular_user = user_model.objects.create_user(
            username="buyer",
            password="pass12345",
        )

    def _valid_payload(self):
        return {
            "name": "Test Runner",
            "slug": "test-runner",
            "brand": "Nike",
            "category": "Lifestyle",
            "price": "12990.00",
            "old_price": "",
            "colorway": "Blue / White",
            "accent_color": "#1495ff",
            "short_description": "Тестовая пара для проверки формы.",
            "description": "Описание тестовой пары кроссовок.",
            "sizes_text": "39, 40, 41, 42",
            "model_path": "sneakers/models/scene.gltf",
            "is_featured": "",
        }

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("sneakers:create"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_regular_user_cannot_open_create_page(self):
        self.client.login(username="buyer", password="pass12345")

        response = self.client.get(reverse("sneakers:create"))

        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_create_sneaker(self):
        self.client.login(username="manager", password="pass12345")

        response = self.client.post(reverse("sneakers:create"), data=self._valid_payload())

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Sneaker.objects.filter(slug="test-runner").exists())

    def test_staff_user_can_open_management_list(self):
        self.client.login(username="manager", password="pass12345")

        response = self.client.get(reverse("sneakers:manage_sneakers"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Управление кроссовками")

    def test_staff_user_can_update_sneaker(self):
        sneaker = Sneaker.objects.first()
        self.client.login(username="manager", password="pass12345")
        payload = self._valid_payload()
        payload["name"] = "Updated Runner"
        payload["slug"] = sneaker.slug

        response = self.client.post(
            reverse("sneakers:edit", kwargs={"pk": sneaker.pk}),
            data=payload,
        )

        self.assertEqual(response.status_code, 302)
        sneaker.refresh_from_db()
        self.assertEqual(sneaker.name, "Updated Runner")

    def test_staff_user_can_delete_sneaker(self):
        sneaker = Sneaker.objects.first()
        self.client.login(username="manager", password="pass12345")

        response = self.client.post(reverse("sneakers:delete", kwargs={"pk": sneaker.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Sneaker.objects.filter(pk=sneaker.pk).exists())


class AccountShoppingTests(TestCase):
    def setUp(self):
        self.sneaker = Sneaker.objects.first()
        self.user = get_user_model().objects.create_user(
            username="customer",
            password="pass12345",
        )

    def test_user_can_register(self):
        response = self.client.post(
            reverse("sneakers:signup"),
            data={
                "username": "newcustomer",
                "email": "new@example.com",
                "password1": "StrongPass12345",
                "password2": "StrongPass12345",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(username="newcustomer").exists())

    def test_logged_in_user_can_add_sneaker_to_cart(self):
        self.client.login(username="customer", password="pass12345")

        response = self.client.post(
            reverse("sneakers:cart_add", kwargs={"pk": self.sneaker.pk}),
            data={"next": reverse("sneakers:cart")},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            CartItem.objects.get(user=self.user, sneaker=self.sneaker).quantity,
            1,
        )

    def test_cart_persists_after_logout(self):
        self.client.login(username="customer", password="pass12345")
        self.client.post(reverse("sneakers:cart_add", kwargs={"pk": self.sneaker.pk}))
        self.client.logout()
        self.client.login(username="customer", password="pass12345")

        response = self.client.get(reverse("sneakers:cart"))

        self.assertContains(response, self.sneaker.name)
        self.assertTrue(CartItem.objects.filter(user=self.user, sneaker=self.sneaker).exists())

    def test_logged_in_user_can_toggle_favorite(self):
        self.client.login(username="customer", password="pass12345")

        response = self.client.post(
            reverse("sneakers:favorite_toggle", kwargs={"pk": self.sneaker.pk}),
            data={"next": reverse("sneakers:favorites")},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Favorite.objects.filter(user=self.user, sneaker=self.sneaker).exists()
        )

    def test_favorite_persists_after_logout(self):
        self.client.login(username="customer", password="pass12345")
        self.client.post(reverse("sneakers:favorite_toggle", kwargs={"pk": self.sneaker.pk}))
        self.client.logout()
        self.client.login(username="customer", password="pass12345")

        response = self.client.get(reverse("sneakers:favorites"))

        self.assertContains(response, self.sneaker.name)
