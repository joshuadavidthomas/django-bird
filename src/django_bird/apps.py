from __future__ import annotations

from contextlib import suppress

import django.template
from django.apps import AppConfig
from django.conf import settings

from ._typing import override


def wrap_loaders(name: str) -> None:
    for template_config in settings.TEMPLATES:
        engine_name = (
            template_config.get("NAME") or template_config["BACKEND"].split(".")[-2]  # type: ignore[attr-defined]
        )
        if engine_name == name:
            options = template_config.setdefault("OPTIONS", {})
            loaders = options.setdefault("loaders", [])  # type: ignore[attr-defined]

            # find the inner-most loaders, which is an iterable of only strings
            while not all(isinstance(loader, str) for loader in loaders):
                for loader in loaders:
                    # if we've found a list or tuple, we aren't yet in the inner-most loaders
                    if isinstance(loader, list | tuple):
                        # reassign `loaders` variable to force the while loop restart
                        loaders = loader

            # if django-bird's loader is the first, we good
            loaders_already_configured = (
                len(loaders) > 0 and "django_bird.loader.BirdLoader" == loaders[0]
            )
            # if django-bird's templatetag is in the builtins, we good
            builtins_already_configured = (
                "django_bird.templatetags.django_bird"
                in options.setdefault("builtins", [])  # type: ignore[attr-defined]
            )

            # if aren't already configured, fallback to using django-bird's wrapper
            if not loaders_already_configured and not builtins_already_configured:
                ...


class manual(AppConfig):
    label = "django_bird"
    name = "django_bird"
    verbose_name = "Bird"

    @override
    def ready(self): ...


class auto(manual):
    default = True

    @override
    def ready(self):
        super().ready()

        wrap_loaders("django")

        # Force re-evaluation of settings.TEMPLATES because EngineHandler caches it.
        with suppress(AttributeError):
            del django.template.engines.templates
            django.template.engines._engines = {}
