from __future__ import annotations

import logging
from pathlib import Path

from django.conf import settings

from .settings import DEFAULT_SETTINGS

pytest_plugins = []


def pytest_configure(config):
    logging.disable(logging.CRITICAL)

    settings.configure(**DEFAULT_SETTINGS, **TEST_SETTINGS)


TEST_SETTINGS = {
    "INSTALLED_APPS": [
        "django_bird",
    ],
    "TEMPLATES": [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [
                Path(__file__).parent / "templates",
            ],
            "OPTIONS": {
                "builtins": [
                    "django.template.defaulttags",
                ],
                "loaders": [
                    "django_bird.loader.BirdLoader",
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                ],
            },
        }
    ],
}
