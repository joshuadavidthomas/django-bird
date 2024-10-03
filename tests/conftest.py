from __future__ import annotations

import logging
import re
from pathlib import Path

import pytest
from django.conf import settings
from django.test import override_settings

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
                    "django_bird.templatetags.django_bird",
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


@pytest.fixture
def template_dirs(tmp_path):
    base_dir = tmp_path / "templates"
    base_dir.mkdir()
    bird_template_dir = base_dir / "bird"
    bird_template_dir.mkdir()
    return {
        "base": base_dir,
        "bird": bird_template_dir,
    }


@pytest.fixture(autouse=True)
def override_templates_settings(template_dirs):
    with override_settings(
        TEMPLATES=[
            settings.TEMPLATES[0]
            | {
                "DIRS": [
                    *settings.TEMPLATES[0]["DIRS"],
                    template_dirs["base"],
                ]
            }
        ]
    ):
        yield


@pytest.fixture
def create_bird_template(template_dirs):
    def func(name, content):
        template = template_dirs["bird"] / f"{name}.html"
        template.write_text(content)
        return template

    return func


@pytest.fixture
def normalize_whitespace():
    def func(text):
        # this makes writing tests much easier, as it gets rid of any
        # existing whitespace that may be present in the template file

        # multiple whitespace characters
        text = re.sub(r"\s+", " ", text)

        # after opening tag, including when there are attributes
        text = re.sub(r"<(\w+)(\s+[^>]*)?\s*>", r"<\1\2>", text)

        # before closing tag
        text = re.sub(r"\s+>", ">", text)

        # after opening tag and before closing tag
        text = re.sub(r">\s+<", "><", text)

        # immediately after opening tag (including attributes) or before closing tag
        text = re.sub(r"(<\w+(?:\s+[^>]*)?>)\s+|\s+(<\/\w+>)", r"\1\2", text)

        return text.strip()

    return func
