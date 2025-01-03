from __future__ import annotations

import pytest
from django.template.base import Node
from django.template.base import NodeList
from django.template.base import Template
from django.template.context import Context
from django.template.engine import Engine
from django.template.loader import get_template

from django_bird.components import components
from django_bird.loader import BIRD_TAG_PATTERN
from django_bird.loader import BirdLoader
from django_bird.staticfiles import AssetType
from django_bird.templatetags.tags.bird import BirdNode

from .utils import TestAsset
from .utils import TestComponent


@pytest.mark.parametrize(
    "template_content,expected_matches",
    [
        ("{% bird button %}", ["button"]),
        ("{% bird alert %}{% bird button %}", ["alert", "button"]),
        ("{% bird 'button' %}", ["button"]),
        ('{% bird "button" %}', ["button"]),
        ("{%bird button%}", ["button"]),
        ("{%    bird    button    %}", ["button"]),
        ("{% endbird button %}", []),
        ("{% birds button %}", []),
        ("<bird:button>", []),
        ("{% extends 'base.html' %}{% bird button %}", ["button"]),
    ],
)
def test_bird_tag_pattern(template_content, expected_matches):
    matches = [
        m.group(1).strip("'\"") for m in BIRD_TAG_PATTERN.finditer(template_content)
    ]
    assert matches == expected_matches


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
    "node,expected_count",
    [
        (Template("{% bird button %}Click me{% endbird %}"), 1),
        (BirdNode(name="button", attrs=[], nodelist=None), 1),
        (
            BirdNode(
                name="button",
                attrs=[],
                nodelist=NodeList(
                    [BirdNode(name="button", attrs=[], nodelist=None)],
                ),
            ),
            1,
        ),
        (type("NodeWithNoneNodelist", (Node,), {"nodelist": None})(), 0),
        (Template("{% bird button %}{% bird button %}{% endbird %}{% endbird %}"), 1),
    ],
)
def test_ensure_components_loaded(node, expected_count, templates_dir):
    button = TestComponent(name="button", content="<button>Click me</button>").create(
        templates_dir
    )

    TestAsset(
        component=button, content=".button { color: blue; }", asset_type=AssetType.CSS
    ).create()
    TestAsset(
        component=button, content="console.log('button');", asset_type=AssetType.JS
    ).create()

    loader = BirdLoader(Engine.get_default())
    context = Context()

    loader._ensure_components_loaded(node, context)

    assert len(components._components) == expected_count
