from __future__ import annotations

import pytest
from django.template import Context
from django.template import Template
from django.template.exceptions import TemplateSyntaxError

from tests.utils import TestComponent


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


def test_var_context_isolation_between_components(create_template, templates_dir):
    """Verify that variables set in one component don't leak into another."""
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
    assert rendered.count("button1") == 2  # Should appear once in each instance


def test_var_context_does_not_leak_outside_component(create_template, templates_dir):
    """Verify that variables set inside a component aren't accessible outside."""
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
    """Verify that variables are properly scoped in nested components."""
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
    """Verify that vars are clean between multiple renders of the same template."""
    TestComponent(
        name="counter",
        content="""
            {% bird:var count='1' %}
            Count: {{ vars.count }}
        """
    ).create(templates_dir)

    template_path = templates_dir / "test.html"
    template_path.write_text("{% bird counter %}{% endbird %}")
    template = create_template(template_path)

    first_render = template.render({})
    second_render = template.render({})
    
    assert "Count: 1" in first_render
    assert "Count: 1" in second_render  # Should be reset, not incremented


def test_var_append_with_nested_components(create_template, templates_dir):
    """Verify that += operator works correctly with nested components."""
    TestComponent(
        name="outer",
        content="""
            {% bird:var message='Hello' %}
            {% bird:var message+=' outer' %}
            Outer: {{ vars.message }}
            {% bird inner %}{% endbird %}
            After: {{ vars.message }}
        """
    ).create(templates_dir)

    TestComponent(
        name="inner",
        content="""
            {% bird:var message='Hello' %}
            {% bird:var message+=' inner' %}
            Inner: {{ vars.message }}
        """
    ).create(templates_dir)

    template_path = templates_dir / "test.html"
    template_path.write_text("{% bird outer %}{% endbird %}")
    template = create_template(template_path)

    rendered = template.render({})
    assert "Outer: Hello outer" in rendered
    assert "Inner: Hello inner" in rendered
    assert "After: Hello outer" in rendered


def test_var_outside_component():
    """Verify that using vars outside a component fails appropriately."""
    template = Template(
        """
        {% load django_bird %}
        {% bird:var x='test' %}
        {{ vars.x }}
        """
    )
    with pytest.raises(TemplateSyntaxError, match=r"\'bird:var\' tag can only be used within a bird component"):
        template.render(Context({}))
