from __future__ import annotations

import pytest
from django.conf import settings
from django.template.base import Template
from django.template.context import Context
from django.template.exceptions import TemplateDoesNotExist
from django.test import override_settings

from django_bird.conf import DJANGO_BIRD_BUILTINS
from django_bird.conf import DJANGO_BIRD_FINDER
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

            assert DJANGO_BIRD_BUILTINS not in options["builtins"]
            assert DJANGO_BIRD_FINDER not in settings.STATICFILES_FINDERS

            yield

    def test_autoconfigure(self, configurator):
        template_options = settings.TEMPLATES[0]["OPTIONS"]

        configurator.autoconfigure()

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
        assert DJANGO_BIRD_BUILTINS not in template_options["builtins"]
        assert DJANGO_BIRD_FINDER not in settings.STATICFILES_FINDERS

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

    @override_settings(
        **{
            "STATICFILES_FINDERS": [
                "django.contrib.staticfiles.finders.FileSystemFinder",
                "django.contrib.staticfiles.finders.AppDirectoriesFinder",
            ],
            "TEMPLATES": [
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ],
                    },
                },
            ],
        }
    )
    def test_startproject_settings(self, configurator, example_template):
        configurator.autoconfigure()

        template_options = settings.TEMPLATES[0]["OPTIONS"]

        assert DJANGO_BIRD_BUILTINS in template_options["builtins"]
        assert DJANGO_BIRD_FINDER in settings.STATICFILES_FINDERS

        with pytest.raises(TemplateDoesNotExist, match=example_template.base.name):
            Template(example_template.content).render(Context({}))
