from __future__ import annotations

import pytest
from django.conf import settings
from django.test import override_settings

from django_bird.conf import DJANGO_BIRD_BUILTINS
from django_bird.conf import DJANGO_BIRD_FINDER
from django_bird.conf import DJANGO_BIRD_LOADER
from django_bird.conf import AppSettings
from django_bird.conf import AutoConfigurator
from django_bird.conf import app_settings


@pytest.mark.default_app_settings
def test_app_settings():
    assert app_settings.COMPONENT_DIRS == []
    assert app_settings.ENABLE_AUTO_CONFIG is True


class TestAutoConfigurator:
    @pytest.fixture
    def configurator(self):
        return AutoConfigurator(app_settings)

    @pytest.fixture(autouse=True)
    def reset_settings(self):
        template_options = settings.TEMPLATES[0]["OPTIONS"]

        assert DJANGO_BIRD_LOADER in template_options["loaders"]
        assert DJANGO_BIRD_BUILTINS in template_options["builtins"]
        assert DJANGO_BIRD_FINDER in settings.STATICFILES_FINDERS

        with override_settings(
            STATICFILES_FINDERS=[
                finder
                for finder in settings.STATICFILES_FINDERS
                if finder != DJANGO_BIRD_FINDER
            ],
            TEMPLATES=[
                settings.TEMPLATES[0]
                | {
                    **settings.TEMPLATES[0],
                    "OPTIONS": {
                        "loaders": [
                            loader
                            for loader in template_options["loaders"]
                            if loader != DJANGO_BIRD_LOADER
                        ],
                        "builtins": [
                            builtin
                            for builtin in template_options["builtins"]
                            if builtin != DJANGO_BIRD_BUILTINS
                        ],
                    },
                }
            ],
        ):
            options = settings.TEMPLATES[0]["OPTIONS"]

            assert DJANGO_BIRD_LOADER not in options["loaders"]
            assert DJANGO_BIRD_BUILTINS not in options["builtins"]
            assert DJANGO_BIRD_FINDER not in settings.STATICFILES_FINDERS

            yield

    def test_autoconfigure(self, configurator):
        template_options = settings.TEMPLATES[0]["OPTIONS"]

        configurator.autoconfigure()

        assert DJANGO_BIRD_LOADER in template_options["loaders"]
        assert DJANGO_BIRD_BUILTINS in template_options["builtins"]
        assert DJANGO_BIRD_FINDER in settings.STATICFILES_FINDERS

    @override_settings(
        DJANGO_BIRD={
            "ENABLE_AUTO_CONFIG": False,
        }
    )
    def test_autoconfigure_disabled(self):
        app_settings = AppSettings()
        template_options = settings.TEMPLATES[0]["OPTIONS"]

        assert app_settings.ENABLE_AUTO_CONFIG is False
        assert DJANGO_BIRD_LOADER not in template_options["loaders"]
        assert DJANGO_BIRD_BUILTINS not in template_options["builtins"]
        assert DJANGO_BIRD_FINDER not in settings.STATICFILES_FINDERS

    def test_configure_loaders(self, configurator):
        template_options = settings.TEMPLATES[0]["OPTIONS"]

        configurator.configure_loaders(template_options)

        assert DJANGO_BIRD_LOADER in template_options["loaders"]

    def test_configure_builtins(self, configurator):
        template_options = settings.TEMPLATES[0]["OPTIONS"]

        configurator.configure_builtins(template_options)

        assert DJANGO_BIRD_BUILTINS in template_options["builtins"]

    def test_configure_staticfiles(self, configurator):
        configurator.configure_staticfiles()

        assert DJANGO_BIRD_FINDER in settings.STATICFILES_FINDERS

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
            assert DJANGO_BIRD_LOADER not in template_options["loaders"]
            assert DJANGO_BIRD_BUILTINS not in template_options["builtins"]

            configurator.autoconfigure()

            assert template_options == expected
