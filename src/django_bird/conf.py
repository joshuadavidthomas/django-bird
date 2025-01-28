from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import final
import warnings

import django.template
from django.conf import settings

from ._typing import override

DJANGO_BIRD_SETTINGS_NAME = "DJANGO_BIRD"

DJANGO_BIRD_BUILTINS = "django_bird.templatetags.django_bird"
DJANGO_BIRD_FINDER = "django_bird.staticfiles.BirdAssetFinder"
DJANGO_BIRD_LOADER = "django_bird.loader.BirdLoader"


@dataclass
class AppSettings:
    COMPONENT_DIRS: list[Path | str] = field(default_factory=list)
    ENABLE_AUTO_CONFIG: bool = True
    ENABLE_BIRD_ATTRS: bool = True
    _configurator: AutoConfigurator = field(init=False)

    def __post_init__(self):
        self._configurator = AutoConfigurator(self)

    @override
    def __getattribute__(self, __name: str) -> object:
        user_settings = getattr(settings, DJANGO_BIRD_SETTINGS_NAME, {})
        return user_settings.get(__name, super().__getattribute__(__name))

    def autoconfigure(self) -> None:
        if not self.ENABLE_AUTO_CONFIG:
            return

        warnings.warn(
            "Auto-configuration is currently enabled by default, but will be disabled by default "
            "in a future release. To silence this warning, explicitly set DJANGO_BIRD['ENABLE_AUTO_CONFIG'] "
            "to True or False in your settings.",
            DeprecationWarning,
            stacklevel=2,
        )
        
        self._configurator.autoconfigure()


@final
class AutoConfigurator:
    def __init__(self, app_settings: AppSettings) -> None:
        self.app_settings = app_settings
        self._configured = False

    def autoconfigure(self) -> None:
        self.configure_templates()
        self.configure_staticfiles()
        self._configured = True

    def configure_templates(self) -> None:
        template_config = None

        for config in settings.TEMPLATES:
            engine_name = config.get("NAME") or config["BACKEND"].split(".")[-2]
            if engine_name == "django":
                template_config = config
                break

        if template_config is None:
            return

        options = template_config.setdefault("OPTIONS", {})

        self.configure_loaders(options)
        self.configure_builtins(options)

        # Force re-evaluation of settings.TEMPLATES because EngineHandler caches it.
        with suppress(AttributeError):
            del django.template.engines.templates
            django.template.engines._engines = {}  # type: ignore[attr-defined]

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
            len(loaders) > 0 and DJANGO_BIRD_LOADER == loaders[0]
        )

        if not loaders_already_configured:
            loaders.insert(0, DJANGO_BIRD_LOADER)

    def configure_builtins(self, options: dict[str, Any]) -> None:
        builtins = options.setdefault("builtins", [])

        builtins_already_configured = DJANGO_BIRD_BUILTINS in builtins

        if not builtins_already_configured:
            builtins.append(DJANGO_BIRD_BUILTINS)

    def configure_staticfiles(self) -> None:
        finders_already_configured = DJANGO_BIRD_FINDER in settings.STATICFILES_FINDERS

        if not finders_already_configured:
            settings.STATICFILES_FINDERS.append(DJANGO_BIRD_FINDER)


app_settings = AppSettings()
