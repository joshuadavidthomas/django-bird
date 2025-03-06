from __future__ import annotations

import pytest
from django.test import override_settings

from django_bird.templates import find_components_in_template
from django_bird.templates import gather_bird_tag_template_usage
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


def test_get_template_names_duplicates():
    with override_settings(DJANGO_BIRD={"COMPONENT_DIRS": ["bird"]}):
        template_names = get_template_names("button")

        template_counts = {}
        for template in template_names:
            template_counts[template] = template_counts.get(template, 0) + 1

        for _, count in template_counts.items():
            assert count == 1


def test_find_components_handles_errors():
    result = find_components_in_template("non_existent_template.html")
    assert result == set()


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
