from __future__ import annotations

from importlib.util import find_spec

from django.apps import AppConfig

from ._typing import override


class DjangoBirdAppConfig(AppConfig):
    label = "django_bird"
    name = "django_bird"
    verbose_name = "Bird"

    @override
    def ready(self):
        from django_bird.components import components
        from django_bird.conf import app_settings

        app_settings.autoconfigure()

        if not find_spec("nanodjango"):
            components.discover_components()
