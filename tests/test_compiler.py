from __future__ import annotations

import pytest

from django_bird.compiler import BirdCompiler


@pytest.fixture
def compiler():
    return BirdCompiler()


def test_compile_no_bird_elements(compiler):
    content = "<div>Hello, world!</div>"
    result = compiler.compile(content)
    assert result == content


def test_compile_bird_button(compiler):
    content = '<div><bird:button class="btn-primary">Click me</bird:button></div>'
    result = compiler.compile(content)
    expected = '<div>{% load django_bootstrap5 %}{% bootstrap_button "Click me" button_class="btn-primary" %}</div>'
    assert result.strip() == expected
