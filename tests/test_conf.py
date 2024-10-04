from __future__ import annotations

import pytest
from django.conf import settings
from django.test import override_settings

from django_bird.conf import AppSettings
from django_bird.conf import TemplateConfigurator
from django_bird.conf import app_settings


def test_app_settings():
    assert app_settings.ENABLE_AUTO_CONFIG is True


@override_settings(
    DJANGO_BIRD={
        "ENABLE_AUTO_CONFIG": False,
    }
)
def test_autoconfigure_disabled():
    app_settings = AppSettings()
    template_options = settings.TEMPLATES[0]["OPTIONS"]

    assert app_settings.ENABLE_AUTO_CONFIG is False
    assert "django_bird.templatetags.django_bird" not in template_options["loaders"]
    assert "django_bird.loader.BirdLoader" not in template_options["builtins"]


class TestTemplateConfigurator:
    DJANGO_BIRD_BUILTINS = "django_bird.templatetags.django_bird"
    DJANGO_BIRD_LOADER = "django_bird.loader.BirdLoader"

    @pytest.fixture
    def configurator(self):
        return TemplateConfigurator(app_settings)

    @pytest.fixture(autouse=True)
    def reset_settings(self):
        template_options = settings.TEMPLATES[0]["OPTIONS"]

        assert self.DJANGO_BIRD_LOADER in template_options["loaders"]
        assert self.DJANGO_BIRD_BUILTINS in template_options["builtins"]

        with override_settings(
            TEMPLATES=[
                settings.TEMPLATES[0]
                | {
                    **settings.TEMPLATES[0],
                    "OPTIONS": {
                        "loaders": [
                            loader
                            for loader in template_options["loaders"]
                            if loader != self.DJANGO_BIRD_LOADER
                        ],
                        "builtins": [
                            builtin
                            for builtin in template_options["builtins"]
                            if builtin != self.DJANGO_BIRD_BUILTINS
                        ],
                    },
                }
            ]
        ):
            options = settings.TEMPLATES[0]["OPTIONS"]

            assert self.DJANGO_BIRD_LOADER not in options["loaders"]
            assert self.DJANGO_BIRD_BUILTINS not in options["builtins"]

            yield

    def test_autoconfigure(self, configurator):
        template_options = settings.TEMPLATES[0]["OPTIONS"]

        configurator.autoconfigure()

        assert self.DJANGO_BIRD_LOADER in template_options["loaders"]
        assert self.DJANGO_BIRD_BUILTINS in template_options["builtins"]

    def test_configure_loaders(self, configurator):
        template_options = settings.TEMPLATES[0]["OPTIONS"]

        configurator.configure_loaders(template_options)

        assert self.DJANGO_BIRD_LOADER in template_options["loaders"]

    def test_configure_builtins(self, configurator):
        template_options = settings.TEMPLATES[0]["OPTIONS"]

        configurator.configure_builtins(template_options)

        assert self.DJANGO_BIRD_BUILTINS in template_options["builtins"]

    def test_configured(self, configurator):
        assert configurator._configured is False

        configurator.autoconfigure()

        assert configurator._configured is True

    @pytest.mark.parametrize(
        "init_options,expected",
        [
            (
                {
                    "builtins": [
                        "django.template.defaulttags",
                    ],
                    "loaders": [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                },
                {
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
            ),
            (
                {
                    "builtins": [
                        "django.template.defaulttags",
                    ],
                    "loaders": [
                        (
                            "django.template.loaders.cached.Loader",
                            [
                                "django.template.loaders.filesystem.Loader",
                                "django.template.loaders.app_directories.Loader",
                            ],
                        ),
                    ],
                },
                {
                    "builtins": [
                        "django.template.defaulttags",
                        "django_bird.templatetags.django_bird",
                    ],
                    "loaders": [
                        (
                            "django.template.loaders.cached.Loader",
                            [
                                "django_bird.loader.BirdLoader",
                                "django.template.loaders.filesystem.Loader",
                                "django.template.loaders.app_directories.Loader",
                            ],
                        ),
                    ],
                },
            ),
            (
                {
                    "builtins": [
                        "django.template.defaulttags",
                    ],
                    "loaders": [
                        (
                            "template_partials.loader.Loader",
                            [
                                (
                                    "django.template.loaders.cached.Loader",
                                    [
                                        "django.template.loaders.filesystem.Loader",
                                        "django.template.loaders.app_directories.Loader",
                                    ],
                                ),
                            ],
                        )
                    ],
                },
                {
                    "builtins": [
                        "django.template.defaulttags",
                        "django_bird.templatetags.django_bird",
                    ],
                    "loaders": [
                        (
                            "template_partials.loader.Loader",
                            [
                                (
                                    "django.template.loaders.cached.Loader",
                                    [
                                        "django_bird.loader.BirdLoader",
                                        "django.template.loaders.filesystem.Loader",
                                        "django.template.loaders.app_directories.Loader",
                                    ],
                                ),
                            ],
                        )
                    ],
                },
            ),
            (
                {
                    "builtins": [
                        "django.template.defaulttags",
                        "django_cotton.templatetags.cotton",
                    ],
                    "loaders": [
                        (
                            "django.template.loaders.cached.Loader",
                            [
                                "django_cotton.cotton_loader.Loader",
                                "django.template.loaders.filesystem.Loader",
                                "django.template.loaders.app_directories.Loader",
                            ],
                        ),
                    ],
                },
                {
                    "builtins": [
                        "django.template.defaulttags",
                        "django_cotton.templatetags.cotton",
                        "django_bird.templatetags.django_bird",
                    ],
                    "loaders": [
                        (
                            "django.template.loaders.cached.Loader",
                            [
                                "django_bird.loader.BirdLoader",
                                "django_cotton.cotton_loader.Loader",
                                "django.template.loaders.filesystem.Loader",
                                "django.template.loaders.app_directories.Loader",
                            ],
                        ),
                    ],
                },
            ),
            (
                {
                    "builtins": [
                        "django.template.defaulttags",
                        "django_cotton.templatetags.cotton",
                    ],
                    "loaders": [
                        (
                            "template_partials.loader.Loader",
                            [
                                (
                                    "django.template.loaders.cached.Loader",
                                    [
                                        "django_cotton.cotton_loader.Loader",
                                        "django.template.loaders.filesystem.Loader",
                                        "django.template.loaders.app_directories.Loader",
                                    ],
                                ),
                            ],
                        )
                    ],
                },
                {
                    "builtins": [
                        "django.template.defaulttags",
                        "django_cotton.templatetags.cotton",
                        "django_bird.templatetags.django_bird",
                    ],
                    "loaders": [
                        (
                            "template_partials.loader.Loader",
                            [
                                (
                                    "django.template.loaders.cached.Loader",
                                    [
                                        "django_bird.loader.BirdLoader",
                                        "django_cotton.cotton_loader.Loader",
                                        "django.template.loaders.filesystem.Loader",
                                        "django.template.loaders.app_directories.Loader",
                                    ],
                                ),
                            ],
                        )
                    ],
                },
            ),
        ],
    )
    def test_template_settings(self, init_options, expected, configurator):
        with override_settings(
            TEMPLATES=[
                settings.TEMPLATES[0]
                | {
                    **settings.TEMPLATES[0],
                    "OPTIONS": init_options,
                }
            ]
        ):
            template_options = settings.TEMPLATES[0]["OPTIONS"]

            assert template_options == init_options
            assert self.DJANGO_BIRD_LOADER not in template_options["loaders"]
            assert self.DJANGO_BIRD_BUILTINS not in template_options["builtins"]

            configurator.autoconfigure()

            assert template_options == expected
