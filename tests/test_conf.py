from __future__ import annotations

import pytest
from django.conf import settings
from django.test import SimpleTestCase
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
class TestAutoConfigure(SimpleTestCase):
    def test_app_settings(self):
        assert app_settings.ENABLE_AUTO_CONFIG is False


class TestTemplateConfigurator:
    DJANGO_BIRD_BUILTINS = "django_bird.templatetags.django_bird"
    DJANGO_BIRD_LOADER = "django_bird.loader.BirdLoader"

    @pytest.fixture
    def configurator(self):
        return TemplateConfigurator(app_settings)

    @pytest.fixture
    def template_options(self):
        return settings.TEMPLATES[0]["OPTIONS"]

    @pytest.fixture(autouse=True)
    def reset_settings(self, template_options):
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

    def test_autoconfigure(self, configurator, template_options):
        configurator.autoconfigure()

        assert self.DJANGO_BIRD_LOADER in template_options["loaders"]
        assert self.DJANGO_BIRD_BUILTINS in template_options["builtins"]

    def test_configure_loaders(self, configurator, template_options):
        configurator.configure_loaders(template_options)

        assert self.DJANGO_BIRD_LOADER in template_options["loaders"]

    def test_configure_builtins(self, configurator, template_options):
        configurator.configure_builtins(template_options)

        assert self.DJANGO_BIRD_BUILTINS in template_options["builtins"]

    def test_configured(self, configurator):
        assert configurator._configured is False

        configurator.autoconfigure()

        assert configurator._configured is True

    def test_app_settings(self, configurator):
        app_settings = AppSettings()
        app_settings._template_configurator = configurator

        assert app_settings._template_configurator._configured is False

        configurator.autoconfigure()

        assert app_settings._template_configurator._configured is True
