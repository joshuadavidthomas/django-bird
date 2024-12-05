from __future__ import annotations

import pytest
from django.template.base import Node
from django.template.base import NodeList
from django.template.base import Template
from django.template.context import Context
from django.template.engine import Engine
from django.template.loader import get_template

from django_bird.loader import BIRD_TAG_PATTERN
from django_bird.loader import BirdLoader
from django_bird.params import Params
from django_bird.templatetags.tags.bird import BirdNode


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


def test_asset_registry(
    create_bird_template, create_bird_asset, create_template, templates_dir
):
    alert = create_bird_template("alert", '<div class="alert">{{ slot }}</div>')
    create_bird_asset(alert, ".alert { color: red; }", "css")
    create_bird_asset(alert, "console.log('alert');", "js")

    badge = create_bird_template("badge", "<span>{{ slot }}</span>")
    create_bird_asset(badge, ".badge { color: blue; }", "css")
    create_bird_asset(badge, "console.log('badge');", "js")

    button = create_bird_template("button", "<button>{{ slot }}</button>")
    create_bird_asset(button, ".button { color: blue; }", "css")
    create_bird_asset(button, "console.log('button');", "js")

    base_path = templates_dir / "base.html"
    base_path.write_text("""
        <html>
        <head>
            <title>Test</title>
            {% bird:css %}
        </head>
        <body>
            {% bird alert %}Base Alert{% endbird %}
            {% block content %}{% endblock %}
            {% bird:js %}
        </body>
        </html>
    """)

    include_path = templates_dir / "include.html"
    include_path.write_text("""
        {% bird badge %}Active{% endbird %}
    """)

    child_path = templates_dir / "child.html"
    child_path.write_text("""
        {% extends 'base.html' %}
        {% block content %}
            {% bird button %}Click me{% endbird %}
            {% include 'include.html' %}
        {% endblock %}
    """)

    template = create_template(child_path)

    engine = template.template.engine
    loader = engine.template_loaders[0]

    components = loader.asset_registry.components

    assert len(components) == 3


@pytest.mark.parametrize(
    "node,expected_count",
    [
        (Template("{% bird button %}Click me{% endbird %}"), 1),
        (BirdNode(name="button", params=Params([]), nodelist=None), 1),
        (
            BirdNode(
                name="button",
                params=Params([]),
                nodelist=NodeList(
                    [BirdNode(name="button", params=Params([]), nodelist=None)],
                ),
            ),
            1,
        ),
        (type("NodeWithNoneNodelist", (Node,), {"nodelist": None})(), 0),
        (Template("{% bird button %}{% bird button %}{% endbird %}{% endbird %}"), 1),
    ],
)
def test_scan_for_components(
    node, expected_count, create_bird_template, create_bird_asset
):
    button = create_bird_template("button", "<button>Click me</button>")
    create_bird_asset(button, ".button { color: blue; }", "css")
    create_bird_asset(button, "console.log('button');", "js")

    loader = BirdLoader(Engine.get_default())
    context = Context()

    loader._scan_for_components(node, context)

    assert len(loader.asset_registry.components) == expected_count
