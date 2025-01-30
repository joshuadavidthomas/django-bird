from __future__ import annotations

import contextlib
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from django.conf import settings
from django.template.backends.django import DjangoTemplates
from django.template.backends.django import Template as DjangoTemplate
from django.template.engine import Engine
from django.test import override_settings
from django.urls import clear_url_caches
from django.urls import include
from django.urls import path

from .settings import DEFAULT_SETTINGS

if TYPE_CHECKING:
    from django_bird.components import Component


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
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                ],
            },
        }
    ],
}


@pytest.fixture(autouse=True)
def setup_urls():
    urlpatterns = [
        path("__bird__/", include("django_bird.urls")),
    ]

    clear_url_caches()

    with override_settings(
        ROOT_URLCONF=type(
            "urls",
            (),
            {"urlpatterns": urlpatterns},
        ),
    ):
        yield

    clear_url_caches()


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


@pytest.fixture(autouse=True)
def data_bird_attr_app_setting(override_app_settings, request):
    enable = "default_app_settings" in request.keywords

    with override_app_settings(ENABLE_BIRD_ATTRS=enable):
        yield


@pytest.fixture
def create_template():
    def _create_template(template_file: Path) -> DjangoTemplate:
        engine = Engine(
            builtins=["django_bird.templatetags.django_bird"],
            dirs=[str(template_file.parent)],
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


@dataclass
class ExampleTemplate:
    base: Path
    include: Path
    template: Path
    used_components: list[Component]
    unused_components: list[Component]

    @property
    def content(self):
        return self.template.read_text()


@pytest.fixture
def example_template(templates_dir):
    from django_bird.components import Component
    from django_bird.staticfiles import AssetType

    from .utils import TestAsset
    from .utils import TestComponent

    button = TestComponent(name="button", content="<button>{{ slot }}</button>").create(
        templates_dir
    )
    TestAsset(
        component=button,
        content=".button { color: blue; }",
        asset_type=AssetType.CSS,
    ).create()
    TestAsset(
        component=button, content="console.log('button');", asset_type=AssetType.JS
    ).create()

    alert = TestComponent(
        name="alert", content='<div class="alert">{{ slot }}</div>'
    ).create(templates_dir)
    TestAsset(
        component=alert, content=".alert { color: red; }", asset_type=AssetType.CSS
    ).create()

    banner = TestComponent(
        name="banner", content="<div {{ attrs }}>{{ slot }}</div>"
    ).create(templates_dir)

    toast = TestComponent(name="toast", content="<div>{{ slot }}</div>").create(
        templates_dir
    )
    TestAsset(
        component=toast,
        content=".toast { color: pink; }",
        asset_type=AssetType.CSS,
    ).create()
    TestAsset(
        component=toast, content="console.log('toast');", asset_type=AssetType.JS
    ).create()

    base_template = templates_dir / "base.html"
    base_template.write_text("""
        <html>
        <head>
            <title>Test</title>
            {% bird:css %}
        </head>
        <body>
            {% bird alert %}Warning{% endbird %}
            {% block content %}{% endblock %}
            {% bird:js %}
        </body>
        </html>
    """)

    include_template = templates_dir / "include.html"
    include_template.write_text("""
        {% bird banner %}Include me{% endbird %}
    """)

    template = templates_dir / "template.html"
    template.write_text("""
        {% extends "base.html" %}
        {% block content %}
            {% include "include.html" %}
            {% bird button %}Click me{% endbird %}
        {% endblock %}
    """)

    return ExampleTemplate(
        base=base_template,
        include=include_template,
        template=template,
        used_components=[
            Component.from_name(alert.name),
            Component.from_name(banner.name),
            Component.from_name(button.name),
        ],
        unused_components=[Component.from_name(toast.name)],
    )


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
def registry():
    from django_bird.components import components

    components.reset()
    yield components
    components.reset()
