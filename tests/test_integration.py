from __future__ import annotations

from contextlib import contextmanager

from django.template import Context
from django.template import Template

from django_bird.components import components
from django_bird.staticfiles import AssetType

from .utils import TestAsset
from .utils import TestComponent


@contextmanager
def discover_components():
    try:
        yield
    finally:
        components.discover_components()


def test_template_inheritance_assets(create_template, templates_dir):
    with discover_components():
        parent = TestComponent(name="parent", content="<div>Parent</div>").create(
            templates_dir
        )
        child = TestComponent(name="child", content="<div>Child</div>").create(
            templates_dir
        )

        parent_css = TestAsset(
            component=parent,
            content=".parent { color: red; }",
            asset_type=AssetType.CSS,
        ).create()
        child_css = TestAsset(
            component=child,
            content=".parent { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

    base_template = templates_dir / "base.html"
    base_template.write_text("""
        {% bird:css %}

        {% bird parent %}Parent Content{% endbird %}
        {% block content %}{% endblock %}
    """)

    template = Template("""
        {% extends 'base.html' %}

        {% block content %}
            {% bird child %}Child Content{% endbird %}
        {% endblock %}
    """)
    rendered = template.render(Context({}))

    assert str(parent_css.file) in rendered
    assert str(child_css.file) in rendered
