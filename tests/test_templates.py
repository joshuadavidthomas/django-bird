from __future__ import annotations

import pytest
from django.test import override_settings

from django_bird.templates import find_components_in_template
from django_bird.templates import gather_bird_tag_template_usage
from django_bird.templates import get_component_directory_names
from django_bird.templates import get_template_names


@pytest.mark.parametrize(
    "name,component_dirs,expected",
    [
        (
            "button",
            [],
            [
                "bird/button/button.html",
                "bird/button/index.html",
                "bird/button.html",
            ],
        ),
        (
            "input.label",
            [],
            [
                "bird/input/label/label.html",
                "bird/input/label/index.html",
                "bird/input/label.html",
                "bird/input.label.html",
            ],
        ),
        (
            "button",
            ["custom", "theme"],
            [
                "custom/button/button.html",
                "custom/button/index.html",
                "custom/button.html",
                "theme/button/button.html",
                "theme/button/index.html",
                "theme/button.html",
                "bird/button/button.html",
                "bird/button/index.html",
                "bird/button.html",
            ],
        ),
    ],
)
def test_get_template_names(name, component_dirs, expected):
    with override_settings(DJANGO_BIRD={"COMPONENT_DIRS": component_dirs}):
        template_names = get_template_names(name)

    assert template_names == expected


def test_get_template_names_invalid():
    template_names = get_template_names("input.label")

    assert "bird/input/label/invalid.html" not in template_names


def test_get_template_names_duplicates(override_app_settings):
    with override_app_settings(COMPONENT_DIRS=["bird"]):
        template_names = get_template_names("button")

        template_counts = {}
        for template in template_names:
            template_counts[template] = template_counts.get(template, 0) + 1

        for _, count in template_counts.items():
            assert count == 1


def test_component_directory_names(override_app_settings):
    assert get_component_directory_names() == ["bird"]

    with override_app_settings(COMPONENT_DIRS=["components"]):
        assert get_component_directory_names() == ["components", "bird"]


def test_find_components_handles_errors():
    result = find_components_in_template("non_existent_template.html")
    assert result == set()


def test_find_components_ignores_django_load_tag(templates_dir):
    """Django's built-in {% load %} tag produces a LoadNode with the same class
    name as django-bird's LoadNode.  The visitor must not crash when it
    encounters the built-in one (which has no ``component_names`` attribute).
    """
    template_file = templates_dir / "django_load_tag.html"
    template_file.write_text("""
    {% load static %}
    <html>
    <body>
        {% bird button %}Click{% endbird %}
    </body>
    </html>
    """)

    result = find_components_in_template(template_file.name)

    assert result == {"button"}


def test_find_components_django_load_and_bird_load_coexist(templates_dir):
    """Both Django's {% load %} and django-bird's {% bird:load %} can appear
    in the same template without conflict.
    """
    template_file = templates_dir / "both_load_tags.html"
    template_file.write_text("""
    {% load static %}
    <html>
    <body>
        {% bird:load modal modal.trigger %}
        {% bird button %}Click{% endbird %}
    </body>
    </html>
    """)

    result = find_components_in_template(template_file.name)

    assert result == {"button", "modal", "modal.trigger"}


def test_find_components_includes_bird_load_declarations(templates_dir):
    template_file = templates_dir / "load_tag_usage.html"
    template_file.write_text("""
    <html>
    <body>
        {% bird:load modal modal.trigger %}
    </body>
    </html>
    """)

    result = find_components_in_template(template_file.name)

    assert result == {"modal", "modal.trigger"}


def test_find_components_handles_encoding_errors(templates_dir):
    binary_file = templates_dir / "binary_file.html"
    with open(binary_file, "wb") as f:
        f.write(b"\x80\x81\x82invalid binary content\xfe\xff")

    valid_file = templates_dir / "valid_file.html"
    valid_file.write_text("""
    <html>
    <body>
        {% bird button %}Button{% endbird %}
    </body>
    </html>
    """)

    results = list(gather_bird_tag_template_usage())

    assert all(str(valid_file) in str(path) for path, _ in results)
