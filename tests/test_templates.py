from __future__ import annotations

import pytest
from django.test import override_settings

from django_bird.templates import BIRD_TAG_PATTERN
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


@pytest.mark.parametrize(
    "template_content,expected_matches",
    [
        ("{% bird button %}", ["button"]),
        ("{% bird alert %}{% bird button %}", ["alert", "button"]),
        ("{% bird 'button' %}", ["'button'"]),
        ('{% bird "button" %}', ['"button"']),
        ("{%bird button%}", ["button"]),
        ("{%    bird    button    %}", ["button"]),
        ("{% endbird button %}", []),
        ("{% birds button %}", []),
        ("<bird:button>", []),
        ("{% extends 'base.html' %}{% bird button %}", ["button"]),
        ("{% bird\n'multiline'\n%}", ["'multiline'"]),
        ('{% bird "line1\nline2" %}', ['"line1\nline2"']),
        ("{% bird   '  whitespace  '  \n%}", ["'  whitespace  '"]),
        ("{% bird 'mixed\"quotes'\n%}", ["'mixed\"quotes'"]),
        ("{% bird content\n%}", ["content"]),
    ],
)
def test_bird_tag_pattern(template_content, expected_matches):
    matches = [m.group(1) for m in BIRD_TAG_PATTERN.finditer(template_content)]
    assert matches == expected_matches
