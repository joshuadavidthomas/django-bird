from __future__ import annotations

import contextlib
import logging
import re
from pathlib import Path

import pytest
from django.conf import settings
from django.template.backends.django import DjangoTemplates
from django.template.backends.django import Template as DjangoTemplate
from django.template.engine import Engine
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
def templates_dir(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    return templates_dir


@pytest.fixture(autouse=True)
def override_templates_settings(templates_dir):
    with override_settings(
        TEMPLATES=[
            settings.TEMPLATES[0]
            | {
                "DIRS": [
                    *settings.TEMPLATES[0]["DIRS"],
                    templates_dir,
                ]
            }
        ]
    ):
        yield


@pytest.fixture
def override_app_settings():
    from django_bird.conf import DJANGO_BIRD_SETTINGS_NAME

    @contextlib.contextmanager
    def _override_app_settings(**kwargs):
        with override_settings(**{DJANGO_BIRD_SETTINGS_NAME: {**kwargs}}):
            yield

    return _override_app_settings


@pytest.fixture
def create_template():
    def _create_template(template_file: Path) -> DjangoTemplate:
        engine = Engine(
            builtins=["django_bird.templatetags.django_bird"],
            dirs=[str(template_file.parent)],
            loaders=["django_bird.loader.BirdLoader"],
        )
        template = engine.get_template(template_file.name)
        backend = DjangoTemplates(
            {
                "NAME": "django",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {
                    "autoescape": True,
                    "debug": False,
                    "context_processors": [],
                },
            }
        )
        return DjangoTemplate(template, backend)

    return _create_template


@pytest.fixture
def normalize_whitespace():
    def func(text: str) -> str:
        """Normalize whitespace in rendered template output"""
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
        # between tags and text content
        text = re.sub(r">\s+([^<])", r">\1", text)
        text = re.sub(r"([^>])\s+<", r"\1<", text)
        return text.strip()

    return func


@pytest.fixture(autouse=True)
def clear_components_registry():
    from django_bird.components import components

    components.clear()
    yield
    components.clear()
