from __future__ import annotations

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
        components.discover_components()
