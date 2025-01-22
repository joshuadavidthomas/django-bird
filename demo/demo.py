# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "dj-angles",
#     "django-bird @ ${PROJECT_ROOT}",
#     "nanodjango",
# ]
# ///
from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from django.shortcuts import render
from django.urls import include
from nanodjango import Django

app = Django(
    ANGLES={
        "default_mapper": "dj_angles.mappers.thirdparty.map_bird",
    },
    DJANGO_BIRD={"ENABLE_AUTO_CONFIG": False},
    EXTRA_APPS=[
        "django_bird",
    ],
    TEMPLATES=[
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
                "context_processors": [
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
                "loaders": [
                    "dj_angles.template_loader.Loader",
                    "django_bird.loader.BirdLoader",
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                ],
            },
        }
    ],
)


@app.route("/", name="index")
def hello_world(request):
    from django_bird.components import components as registry

    registry.discover_components()
    components = list(registry._components.values())
    return render(
        request,
        "index.html",
        {
            "components": sorted(components, key=lambda component: component.name),
        },
    )


@app.route("<str:component_name>/", name="component")
def component(request, component_name):
    from django_bird.components import components as registry

    registry.discover_components()
    components = list(registry._components.values())
    component = registry.get_component(component_name)
    return render(
        request,
        "component.html",
        {
            "components": sorted(components, key=lambda component: component.name),
            "component": component,
        },
    )


app.route("__bird__/", include=include("django_bird.urls"))


def main(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("host", default="0:8000", nargs="?")
    args = parser.parse_args(argv)
    return app.run(args.host)


if __name__ == "__main__":
    raise SystemExit(main())
