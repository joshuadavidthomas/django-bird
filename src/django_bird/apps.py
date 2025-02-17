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
        from django_bird.conf import app_settings
        from django_bird.plugins import pm

        for init_handler in pm.hook.ready(app_settings=app_settings):
            init_handler()
