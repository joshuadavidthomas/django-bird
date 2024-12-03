from __future__ import annotations

import pytest
from django.template.loader import get_template


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

    child_path = templates_dir / "child.html"
    child_path.write_text("""
        {% extends 'base.html' %}
        {% block content %}
            {% bird button %}Click me{% endbird %}
        {% endblock %}
    """)

    template = create_template(child_path)

    engine = template.template.engine
    loader = engine.template_loaders[0]

    components = loader.asset_registry.components

    assert len(components) == 2


def test_asset_registry_extends_nonexistent(
    create_bird_template, create_bird_asset, create_template, templates_dir
):
    button = create_bird_template("button", "<button>{{ slot }}</button>")
    create_bird_asset(button, ".button { color: blue; }", "css")
    create_bird_asset(button, "console.log('button');", "js")

    child_path = templates_dir / "child.html"
    child_path.write_text("""
        {% extends 'base.html' %}
        {% block content %}
            {% bird button %}Click me{% endbird %}
        {% endblock %}
    """)

    template = create_template(child_path)

    engine = template.template.engine
    loader = engine.template_loaders[0]

    components = loader.asset_registry.components

    assert len(components) == 1
