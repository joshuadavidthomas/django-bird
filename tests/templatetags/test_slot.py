from __future__ import annotations

import pytest
from django.template import Context
from django.template import Template
from django.template.exceptions import TemplateSyntaxError

from django_bird.templatetags.tags.slot import parse_slot_name
from tests.utils import TestComponent
from tests.utils import TestComponentCase


@pytest.mark.parametrize(
    "bits,expected",
    [
        (["slot"], "default"),
        (["slot", "foo"], "foo"),
        (["slot", "'foo'"], "foo"),
        (["slot", '"foo"'], "foo"),
        (["slot", 'name="foo"'], "foo"),
        (["slot", "name='foo'"], "foo"),
    ],
)
def test_parse_slot_name(bits, expected):
    assert parse_slot_name(bits) == expected


def test_parse_slot_name_no_args():
    with pytest.raises(TemplateSyntaxError):
        assert parse_slot_name([])


class TestTemplateTag:
    @pytest.mark.parametrize(
        "component_content",
        [
            "{{ slot }}",
            "{% bird:slot %}{% endbird:slot %}",
            "{% bird:slot default %}{% endbird:slot %}",
            "{% bird:slot 'default' %}{% endbird:slot %}",
            '{% bird:slot "default" %}{% endbird:slot %}',
            "{% bird:slot name=default %}{% endbird:slot %}",
            "{% bird:slot name='default' %}{% endbird:slot %}",
            '{% bird:slot name="default" %}{% endbird:slot %}',
        ],
    )
    def test_default_slot(self, component_content, templates_dir, normalize_whitespace):
        test_case = TestComponentCase(
            component=TestComponent(
                name="test",
                content=component_content,
            ),
            template_content="{% bird test %}Content{% endbird %}",
            template_context={"slot": "Content"},
            expected="Content",
        )
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    def test_default_content(self, templates_dir, normalize_whitespace):
        test_case = TestComponentCase(
            component=TestComponent(
                name="test",
                content="""
                    <button>
                        {% bird:slot leading-icon %}
                            <span>Default icon</span>
                        {% endbird:slot %}

                        {% bird:slot %}
                            Click me
                        {% endbird:slot %}
                    </button>
                """,
            ),
            template_content="{% bird test %}{% endbird %}",
            expected="<button><span>Default icon</span>Click me</button>",
        )
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context({}))

        assert normalize_whitespace(rendered) == test_case.expected

    def test_default_content_override(self, templates_dir, normalize_whitespace):
        test_case = TestComponentCase(
            component=TestComponent(
                name="test",
                content="""
                    <button>
                        {% bird:slot leading-icon %}
                            <span>Default icon</span>
                        {% endbird:slot %}

                        {% bird:slot %}
                            Click me
                        {% endbird:slot %}
                    </button>
                """,
            ),
            template_content="""
                {% bird test %}
                    {% bird:slot leading-icon %}→{% endbird:slot %}
                    Submit
                {% endbird %}
            """,
            expected="<button>→ Submit</button>",
        )
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context({}))

        assert normalize_whitespace(rendered) == test_case.expected

    @pytest.mark.parametrize(
        "component_content",
        [
            "{{ slots.named_slot }}",
            "{% bird:slot named_slot %}{% endbird:slot %}",
            "{% bird:slot name=named_slot %}{% endbird:slot %}",
        ],
    )
    def test_named_slot(self, component_content, templates_dir, normalize_whitespace):
        test_case = TestComponentCase(
            component=TestComponent(
                name="test",
                content=component_content,
            ),
            template_content="""
                {% bird test %}
                    {% bird:slot named_slot %}{% endbird:slot %}
                {% endbird %}
            """,
            template_context={
                "slots": {
                    "named_slot": "Content",
                },
            },
            expected="Content",
        )
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Outer slot replacement",
                component=TestComponent(
                    name="test",
                    content="""
                        {% bird:slot outer %}
                            Outer {% bird:slot inner %}Inner{% endbird:slot %} Content
                        {% endbird:slot %}
                    """,
                ),
                template_content="""
                    {% bird test %}
                        {% bird:slot outer %}Replaced Content{% endbird:slot %}
                    {% endbird %}
                """,
                expected="Replaced Content",
            ),
            TestComponentCase(
                description="Inner slot replacement",
                component=TestComponent(
                    name="test",
                    content="""
                        {% bird:slot outer %}
                            Outer {% bird:slot inner %}Inner{% endbird:slot %} Content
                        {% endbird:slot %}
                    """,
                ),
                template_content="""
                    {% bird test %}
                        {% bird:slot inner %}Replaced Content{% endbird:slot %}
                    {% endbird %}
                """,
                expected="Outer Replaced Content Content",
            ),
            TestComponentCase(
                description="Both slots replaced",
                component=TestComponent(
                    name="test",
                    content="""
                        {% bird:slot outer %}
                            Outer {% bird:slot inner %}Inner{% endbird:slot %} Content
                        {% endbird:slot %}
                    """,
                ),
                template_content="""
                    {% bird test %}
                        {% bird:slot outer %}
                            New {% bird:slot inner %}Nested{% endbird:slot %} Text
                        {% endbird:slot %}
                    {% endbird %}
                """,
                expected="New Nested Text",
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_nested_slots(self, test_case, templates_dir, normalize_whitespace):
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Variable in slot",
                component=TestComponent(
                    name="test",
                    content="{% bird:slot %}{% endbird:slot %}",
                ),
                template_content="{% bird test %}{{ message }}{% endbird %}",
                template_context={"message": "Hello World"},
                expected="Hello World",
            ),
            TestComponentCase(
                description="Nested variable in slot",
                component=TestComponent(
                    name="test",
                    content="{% bird:slot %}{% endbird:slot %}",
                ),
                template_content="{% bird test %}{{ user.name }}{% endbird %}",
                template_context={"user": {"name": "John"}},
                expected="John",
            ),
            TestComponentCase(
                description="Template tag in slot",
                component=TestComponent(
                    name="test",
                    content="{% bird:slot %}{% endbird:slot %}",
                ),
                template_content="{% bird test %}{% if show %}Show{% endif %}{% endbird %}",
                template_context={"show": True},
                expected="Show",
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_template_content(self, test_case, templates_dir, normalize_whitespace):
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    def test_too_many_args(self):
        with pytest.raises(TemplateSyntaxError):
            Template("{% bird:slot too many args %}{% endbird:slot %}")
