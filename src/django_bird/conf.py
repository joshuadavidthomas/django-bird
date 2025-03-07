from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from django.conf import settings

from ._typing import override
from .utils import unique_ordered

DJANGO_BIRD_SETTINGS_NAME = "DJANGO_BIRD"

DJANGO_BIRD_BUILTINS = "django_bird.templatetags.django_bird"
DJANGO_BIRD_FINDER = "django_bird.staticfiles.BirdAssetFinder"


@dataclass
class AppSettings:
    ADD_ASSET_PREFIX: bool | None = None
    COMPONENT_DIRS: list[Path | str] = field(default_factory=list)
    ENABLE_BIRD_ATTRS: bool = True

    @override
    def __getattribute__(self, __name: str) -> object:
        user_settings = getattr(settings, DJANGO_BIRD_SETTINGS_NAME, {})
        return user_settings.get(__name, super().__getattribute__(__name))

    def get_component_directory_names(self):
        return unique_ordered([*self.COMPONENT_DIRS, "bird"])


app_settings = AppSettings()
