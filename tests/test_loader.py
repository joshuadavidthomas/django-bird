from __future__ import annotations

import pytest
from django.conf import settings
from django.template.engine import Engine
from django.template.loader import get_template
from django.test import override_settings
from django_bird.loader import BirdLoader


def test_bird_loader_deprecation_warning():
    with pytest.warns(DeprecationWarning, match=(
        "BirdLoader is deprecated and will be removed in a future version. "
        "Please remove 'django_bird.loader.BirdLoader' from your TEMPLATES setting "
        "in settings.py and use Django's built-in 'django.template.loaders.filesystem.Loader' instead."
    )):
        BirdLoader(Engine())


@pytest.mark.parametrize(
    "template_name",
    (
        "with_bird.html",
        "without_bird.html",
    ),
)
def test_render_template(template_name):
    context = {
        "title": "Test Title",
        "content": "Test Content",
    }

    template = get_template(template_name)
    rendered = template.render(context)

    assert rendered


@pytest.mark.parametrize(
    "loaders",
    [
        [
            "django_bird.loader.BirdLoader",
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
        [
            "django.template.loaders.filesystem.Loader",
            "django_bird.loader.BirdLoader",
            "django.template.loaders.app_directories.Loader",
        ],
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
            "django_bird.loader.BirdLoader",
        ],
    ],
)
def test_loader_order(loaders, example_template, registry):
    registry.discover_components()

    with override_settings(
        TEMPLATES=[
            settings.TEMPLATES[0]
            | {
                **settings.TEMPLATES[0],
                "OPTIONS": {
                    **settings.TEMPLATES[0]["OPTIONS"],
                    "loaders": loaders,
                },
            }
        ]
    ):
        rendered = get_template(example_template.template.name).render({})

    assert all(
        asset.url in rendered
        for component in example_template.used_components
        for asset in component.assets
    )
    assert not any(
        asset.url in rendered
        for component in example_template.unused_components
        for asset in component.assets
    )
