from __future__ import annotations

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
def create_bird_dir(templates_dir):
    def func(name):
        bird_template_dir = templates_dir / name
        bird_template_dir.mkdir(exist_ok=True)
        return bird_template_dir

    return func


@pytest.fixture
def create_bird_template(create_bird_dir):
    def func(name, content, sub_dir=None, bird_dir_name="bird"):
        bird_dir = create_bird_dir(bird_dir_name)
        if sub_dir is not None:
            dir = bird_dir / sub_dir
            dir.mkdir()
        else:
            dir = bird_dir
        template = dir / f"{name}.html"
        template.write_text(content)
        return template

    return func


@pytest.fixture
def create_bird_asset():
    def func(component_template: Path, content: str, asset_type: str):
        component_dir = component_template.parent
        component_name = component_template.stem
        asset_file = component_dir / f"{component_name}.{asset_type}"
        asset_file.write_text(content)
        return asset_file

    return func


@pytest.fixture
def create_template():
    def _create_template(template_file: Path) -> DjangoTemplate:
        engine = Engine(
            builtins=["django_bird.templatetags.django_bird"],
            dirs=[str(template_file.parent)],
            loaders=["django_bird.loader.BirdLoader"],
        )
        print(f"Engine dirs: {engine.dirs}")  # Debug print
        print(f"Looking for template: {template_file.name}")  # Debug print
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


@pytest.fixture(autouse=True)
def clear_registry():
    from django_bird.components import components

    components.clear()
    yield
    components.clear()
