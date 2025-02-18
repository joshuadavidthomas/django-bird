from __future__ import annotations

import warnings
from contextlib import suppress
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import final

import django.template
from django.conf import settings

from django_bird import hookimpl

from ._typing import override
from .utils import unique_ordered

DJANGO_BIRD_SETTINGS_NAME = "DJANGO_BIRD"


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
            "Autoconfiguration of django-bird is deprecated and has been moved to the "
            "django-bird-autoconf plugin. Please install the new plugin from PyPI in your "
            "project if you wish to keep this behavior, as this will be removed from the "
            "core library in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._configurator.autoconfigure()

    def get_component_directory_names(self):
        return unique_ordered([*self.COMPONENT_DIRS, "bird"])


@hookimpl
def ready():
    app_settings.autoconfigure()


DJANGO_BIRD_BUILTINS = "django_bird.templatetags.django_bird"
DJANGO_BIRD_FINDER = "django_bird.staticfiles.BirdAssetFinder"


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

        self.configure_builtins(options)

        # Force re-evaluation of settings.TEMPLATES because EngineHandler caches it.
        with suppress(AttributeError):  # pragma: no cover
            del django.template.engines.templates
            django.template.engines._engines = {}  # type:ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]

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
