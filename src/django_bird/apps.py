from __future__ import annotations

from typing import final

from django.apps import AppConfig

from ._typing import override


@final
class DjangoBirdAppConfig(AppConfig):
    label = "django_bird"
    name = "django_bird"
    verbose_name = "Bird"

    @override
    def ready(self):
        from django_bird.components import components
        from django_bird.conf import app_settings
        from django_bird.plugins import pm
        from django_bird.staticfiles import asset_types

        for pre_ready in pm.hook.pre_ready():
            pre_ready()

        app_settings.autoconfigure()
        pm.hook.register_asset_types(register_type=asset_types.register_type)
        components.discover_components()

        for ready in pm.hook.ready():
            ready()
