from __future__ import annotations

import pytest
from django.template import Context
from django.template import Template
from django.template.exceptions import TemplateSyntaxError


def test_basic_assignment():
    template = Template(
        "{% load django_bird %}{% bird:var x='hello' %}{{ vars.x }}{% endbird:var x %}"
    )
    rendered = template.render(Context({}))
    assert rendered == "hello"


def test_append_to_variable():
    template = Template(
        """
        {% load django_bird %}
        {% bird:var x='hello' %}
        {% bird:var x+=' world' %}
        {{ vars.x }}
        {% endbird:var x %}
        """
    )
    rendered = template.render(Context({}))
    assert rendered.strip() == "hello world"


def test_multiple_variables():
    template = Template(
        """
        {% load django_bird %}
        {% bird:var x='hello' %}
        {% bird:var y=' world' %}
        {{ vars.x }}{{ vars.y }}
        {% endbird:var x %}
        {% endbird:var y %}
        """
    )
    rendered = template.render(Context({}))
    assert rendered.strip() == "hello world"


def test_variable_cleanup():
    template = Template(
        """
        {% load django_bird %}
        {% bird:var x='hello' %}
        {% endbird:var x %}
        {{ vars.x|default:'cleaned' }}
        """
    )
    rendered = template.render(Context({}))
    assert rendered.strip() == "cleaned"


def test_append_to_nonexistent_variable():
    template = Template(
        """
        {% load django_bird %}
        {% bird:var x+='world' %}
        {{ vars.x }}
        {% endbird:var x %}
        """
    )
    rendered = template.render(Context({}))
    assert rendered.strip() == "world"


def test_variable_with_template_variable():
    template = Template(
        """
        {% load django_bird %}
        {% bird:var greeting='Hello ' %}
        {% bird:var greeting+=name %}
        {{ vars.greeting }}
        {% endbird:var greeting %}
        """
    )
    rendered = template.render(Context({"name": "Django"}))
    assert rendered.strip() == "Hello Django"


@pytest.mark.parametrize(
    ("template_str", "expected_error"),
    [
        (
            "{% load django_bird %}{% bird:var %}",
            r"\'bird:var\' tag requires an assignment",
        ),
        (
            "{% load django_bird %}{% bird:var invalid_syntax %}",
            r"Invalid assignment in \'bird:var\' tag: invalid_syntax\. Expected format: bird:var variable=\'value\' or bird:var variable\+=\'value\'\.",
        ),
        (
            "{% load django_bird %}{% endbird:var %}",
            r"endbird:var tag requires a variable name",
        ),
    ],
)
def test_syntax_errors(template_str: str, expected_error: str):
    with pytest.raises(TemplateSyntaxError, match=expected_error):
        Template(template_str)
