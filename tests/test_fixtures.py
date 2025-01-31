from __future__ import annotations

from django.template.loader import get_template

from .utils import TestComponent


def test_test_component(templates_dir):
    name = "foo"
    content = "<div>bar</div>"

    TestComponent(name=name, content=content).create(templates_dir)

    template = get_template(f"bird/{name}.html")

    assert template
    assert template.render({}) == content
