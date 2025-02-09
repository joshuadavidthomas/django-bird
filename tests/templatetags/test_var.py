from __future__ import annotations

import pytest
from django import template
from django.template import Context
from django.template import Template
from django.template.base import Parser
from django.template.base import Token
from django.template.base import TokenType
from django.template.exceptions import TemplateSyntaxError

from django_bird.templatetags.tags.var import END_TAG
from django_bird.templatetags.tags.var import TAG
from django_bird.templatetags.tags.var import do_end_var
from django_bird.templatetags.tags.var import do_var
from tests.utils import TestComponent


def test_do_var_no_args():
    start_token = Token(TokenType.BLOCK, TAG)

    with pytest.raises(template.TemplateSyntaxError):
        do_var(Parser([]), start_token)


def test_do_end_var_no_args():
    start_token = Token(TokenType.BLOCK, END_TAG)

    with pytest.raises(template.TemplateSyntaxError):
        do_end_var(Parser([]), start_token)


def test_basic_assignment():
    template = Template("""
        {% load django_bird %}
        {% bird:var x='hello' %}
        {{ vars.x }}
    """)

    rendered = template.render(Context({}))

    assert rendered.strip() == "hello"


def test_append_to_variable():
    template = Template("""
        {% load django_bird %}
        {% bird:var x='hello' %}
        {% bird:var x+=' world' %}
        {{ vars.x }}
    """)

    rendered = template.render(Context({}))

    assert rendered.strip() == "hello world"


def test_multiple_variables():
    template = Template("""
        {% load django_bird %}
        {% bird:var x='hello' %}
        {% bird:var y=' world' %}
        {{ vars.x }}{{ vars.y }}
    """)

    rendered = template.render(Context({}))

    assert rendered.strip() == "hello world"


def test_append_to_nonexistent_variable():
    template = Template("""
        {% load django_bird %}
        {% bird:var x+='world' %}
        {{ vars.x }}
    """)

    rendered = template.render(Context({}))

    assert rendered.strip() == "world"


def test_variable_with_template_variable():
    template = Template("""
        {% load django_bird %}
        {% bird:var greeting='Hello ' %}
        {% bird:var greeting+=name %}
        {{ vars.greeting }}
    """)

    rendered = template.render(Context({"name": "Django"}))

    assert rendered.strip() == "Hello Django"


def test_explicit_var_cleanup():
    template = Template("""
        {% load django_bird %}
        {% bird:var x='hello' %}
        Before: {{ vars.x }}
        {% endbird:var x %}
        After: {{ vars.x|default:'cleaned' }}
    """)

    rendered = template.render(Context({}))

    assert "Before: hello" in rendered
    assert "After: cleaned" in rendered


def test_reseting_var():
    template = Template("""
        {% load django_bird %}
        {% bird:var x='hello' %}
        Before: {{ vars.x }}
        {% bird:var x=None %}
        After: {{ vars.x|default:'cleaned' }}
    """)

    rendered = template.render(Context({}))

    assert "Before: hello" in rendered
    assert "After: cleaned" in rendered


def test_explicit_var_cleanup_with_multiple_vars():
    template = Template("""
        {% load django_bird %}
        {% bird:var x='hello' %}
        {% bird:var y='world' %}
        Before: {{ vars.x }} {{ vars.y }}
        {% endbird:var x %}
        Middle: {{ vars.x|default:'cleaned' }} {{ vars.y }}
        {% endbird:var y %}
        After: {{ vars.x|default:'cleaned' }} {{ vars.y|default:'cleaned' }}
    """)

    rendered = template.render(Context({}))

    assert "Before: hello world" in rendered
    assert "Middle: cleaned world" in rendered
    assert "After: cleaned cleaned" in rendered


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
    ],
)
def test_syntax_errors(template_str: str, expected_error: str):
    with pytest.raises(TemplateSyntaxError, match=expected_error):
        Template(template_str)


def test_var_context_isolation_between_components(create_template, templates_dir):
    TestComponent(
        name="button",
        content="""
            {% bird:var x='button1' %}
            {{ vars.x }}
        """,
    ).create(templates_dir)

    template_path = templates_dir / "test.html"
    template_path.write_text("""
        {% bird button %}{% endbird %}
        {% bird button %}{% endbird %}
    """)
    template = create_template(template_path)

    rendered = template.render({})

    assert "button1" in rendered
    assert rendered.count("button1") == 2


def test_var_context_does_not_leak_outside_component(create_template, templates_dir):
    TestComponent(
        name="button",
        content="""
            {% bird:var x='button1' %}
            Inner: {{ vars.x }}
        """,
    ).create(templates_dir)

    template_path = templates_dir / "test.html"
    template_path.write_text("""
        {% bird button %}{% endbird %}
        Outer: {{ vars.x|default:'not accessible' }}
    """)
    template = create_template(template_path)

    rendered = template.render({})

    assert "Inner: button1" in rendered
    assert "Outer: not accessible" in rendered


def test_var_context_isolation_nested_components(create_template, templates_dir):
    TestComponent(
        name="outer",
        content="""
            {% bird:var x='outer' %}
            Outer: {{ vars.x }}
            {% bird inner %}{% endbird %}
            After Inner: {{ vars.x }}
        """,
    ).create(templates_dir)
    TestComponent(
        name="inner",
        content="""
            {% bird:var x='inner' %}
            Inner: {{ vars.x }}
        """,
    ).create(templates_dir)

    template_path = templates_dir / "test.html"
    template_path.write_text("""
        {% bird outer %}{% endbird %}
    """)
    template = create_template(template_path)

    rendered = template.render({})

    assert "Outer: outer" in rendered
    assert "Inner: inner" in rendered
    assert "After Inner: outer" in rendered


def test_var_context_clean_between_renders(create_template, templates_dir):
    TestComponent(
        name="counter",
        content="""
            {% bird:var count='1' %}
            Count: {{ vars.count }}
        """,
    ).create(templates_dir)

    template_path = templates_dir / "test.html"
    template_path.write_text("{% bird counter %}{% endbird %}")
    template = create_template(template_path)

    first_render = template.render({})
    second_render = template.render({})

    assert "Count: 1" in first_render
    assert "Count: 1" in second_render


def test_var_append_with_nested_components(create_template, templates_dir):
    TestComponent(
        name="outer",
        content="""
            {% bird:var message='Hello' %}
            {% bird:var message+=' outer' %}
            Outer: {{ vars.message }}
            {% bird inner %}{% endbird %}
            After: {{ vars.message }}
        """,
    ).create(templates_dir)
    TestComponent(
        name="inner",
        content="""
            {% bird:var message='Hello' %}
            {% bird:var message+=' inner' %}
            Inner: {{ vars.message }}
        """,
    ).create(templates_dir)

    template_path = templates_dir / "test.html"
    template_path.write_text("{% bird outer %}{% endbird %}")
    template = create_template(template_path)

    rendered = template.render({})

    assert "Outer: Hello outer" in rendered
    assert "Inner: Hello inner" in rendered
    assert "After: Hello outer" in rendered
