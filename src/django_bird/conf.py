from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

import django.template
from django.conf import settings

from ._typing import override

DJANGO_BIRD_SETTINGS_NAME = "DJANGO_BIRD"


@dataclass
class AppSettings:
    COMPONENT_DIRS: list[Path | str] = field(default_factory=list)
    ENABLE_AUTO_CONFIG: bool = True
    _template_configurator: TemplateConfigurator = field(init=False)

    def __post_init__(self):
        self._template_configurator = TemplateConfigurator(self)

    @override
    def __getattribute__(self, __name: str) -> object:
        user_settings = getattr(settings, DJANGO_BIRD_SETTINGS_NAME, {})
        return user_settings.get(__name, super().__getattribute__(__name))  # pyright: ignore[reportAny]

    def autoconfigure(self) -> None:
        if not self.ENABLE_AUTO_CONFIG:
            return

        self._template_configurator.autoconfigure()


class TemplateConfigurator:
    def __init__(self, app_settings: AppSettings, engine_name: str = "django") -> None:
        self.app_settings = app_settings
        self.engine_name = engine_name
        self._configured = False

    def autoconfigure(self) -> None:
        for template_config in settings.TEMPLATES:
            engine_name = (
                template_config.get("NAME") or template_config["BACKEND"].split(".")[-2]
            )
            if engine_name != self.engine_name:
                return

        options = template_config.setdefault("OPTIONS", {})

        self.configure_loaders(options)
        self.configure_builtins(options)

        # Force re-evaluation of settings.TEMPLATES because EngineHandler caches it.
        with suppress(AttributeError):
            del django.template.engines.templates
            django.template.engines._engines = {}  # type: ignore[attr-defined]

        self._configured = True

    def configure_loaders(self, options: dict[str, Any]) -> None:
        loaders = options.setdefault("loaders", [])

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

        if not loaders_already_configured:
            loaders.insert(0, "django_bird.loader.BirdLoader")

    def configure_builtins(self, options: dict[str, Any]) -> None:
        builtins = options.setdefault("builtins", [])

        builtins_already_configured = "django_bird.templatetags.django_bird" in builtins

        if not builtins_already_configured:
            builtins.append("django_bird.templatetags.django_bird")


app_settings = AppSettings()
