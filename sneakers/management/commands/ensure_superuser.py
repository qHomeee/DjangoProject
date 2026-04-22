import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates or promotes a superuser from environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME") or os.environ.get(
            "ADMIN_USERNAME"
        )
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL") or os.environ.get(
            "ADMIN_EMAIL",
            "",
        )
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD") or os.environ.get(
            "ADMIN_PASSWORD"
        )
        reset_password = os.environ.get(
            "DJANGO_SUPERUSER_RESET_PASSWORD",
            "False",
        ).lower() in {"1", "true", "yes", "on"}

        if not username or not password:
            self.stdout.write(
                "Superuser creation skipped: DJANGO_SUPERUSER_USERNAME and "
                "DJANGO_SUPERUSER_PASSWORD are not set."
            )
            return

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        changed = False
        if created:
            user.set_password(password)
            changed = True
        elif reset_password:
            user.set_password(password)
            changed = True

        if email and user.email != email:
            user.email = email
            changed = True
        if not user.is_staff:
            user.is_staff = True
            changed = True
        if not user.is_superuser:
            user.is_superuser = True
            changed = True

        if changed:
            user.save()

        action = "created" if created else "already exists"
        self.stdout.write(self.style.SUCCESS(f"Superuser {username} {action}."))
