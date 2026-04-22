"""ASGI config for sneaker_store project."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sneaker_store.settings")

application = get_asgi_application()
