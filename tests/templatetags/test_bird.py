from __future__ import annotations

import pytest
from django.template import Context
from django.template import Library
from django.template import Template
from django.template.base import Parser
from django.template.base import Token
from django.template.base import TokenType
from django.template.engine import Engine
from django.template.exceptions import TemplateDoesNotExist
from django.template.exceptions import TemplateSyntaxError

from django_bird.components import Component
from django_bird.params import Param
from django_bird.params import Value
from django_bird.templatetags.tags.bird import END_TAG
from django_bird.templatetags.tags.bird import TAG
from django_bird.templatetags.tags.bird import BirdNode
from django_bird.templatetags.tags.bird import do_bird
from tests.utils import TestComponent
from tests.utils import TestComponentCase


class TestTagParsing:
    @pytest.mark.parametrize(
        "name,expected",
        [
            ("button", "button"),
            ("'button'", "'button'"),
            ('"button"', '"button"'),
            ("button.label", "button.label"),
        ],
    )
    def test_name_do_bird(self, name, expected):
        start_token = Token(TokenType.BLOCK, f"{TAG} {name}")
        end_token = Token(TokenType.BLOCK, f"{END_TAG} {name}")

        parser = Parser([end_token])

        node = do_bird(parser, start_token)

        assert node.name == expected

    def test_missing_name_do_bird(self):
        start_token = Token(TokenType.BLOCK, TAG)
        end_token = Token(TokenType.BLOCK, END_TAG)

        parser = Parser([end_token])

        with pytest.raises(TemplateSyntaxError):
            do_bird(parser, start_token)

    @pytest.mark.parametrize(
        "params,expected_attrs",
        [
            (
                "class='btn'",
                [Param(name="class", value=Value("btn", quoted=True))],
            ),
            (
                'class="btn"',
                [Param(name="class", value=Value("btn", quoted=True))],
            ),
            (
                "class='btn' id='my-btn'",
                [
                    Param(name="class", value=Value("btn", quoted=True)),
                    Param(name="id", value=Value("my-btn", quoted=True)),
                ],
            ),
            (
                "disabled",
                [Param(name="disabled", value=Value(True))],
            ),
            (
                "class=dynamic",
                [Param(name="class", value=Value("dynamic", quoted=False))],
            ),
            (
                "class=item.name id=user.id",
                [
                    Param(name="class", value=Value("item.name", quoted=False)),
                    Param(name="id", value=Value("user.id", quoted=False)),
                ],
            ),
        ],
    )
    def test_attrs_do_bird(self, params, expected_attrs):
        start_token = Token(TokenType.BLOCK, f"{TAG} button {params}")
        end_token = Token(TokenType.BLOCK, f"{END_TAG} button")

        parser = Parser([end_token])

        node = do_bird(parser, start_token)

        assert node.attrs == expected_attrs

    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Basic component name",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button %}
                        Click me
                    {% endbird %}
                """,
                expected="<button>Click me</button>",
            ),
            TestComponentCase(
                description="Single-quoted component name",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird 'button' %}
                        Click me
                    {% endbird %}
                """,
                expected="<button>Click me</button>",
            ),
            TestComponentCase(
                description="Double-quoted component name",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird "button" %}
                        Click me
                    {% endbird %}
                """,
                expected="<button>Click me</button>",
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_basic_name_templatetag(
        self, test_case, templates_dir, normalize_whitespace
    ):
        test_case.component.create(templates_dir)

        template = Template(
            test_case.template_content,
        )
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    def test_nested_name_templatetag(self, templates_dir, normalize_whitespace):
        test_case = TestComponentCase(
            description="Nested component name",
            component=TestComponent(
                name="label",
                content="""
                    <span>
                        {{ slot }}
                    </span>
                """,
                sub_dir="button",
            ),
            template_content="""
                {% bird button.label %}
                    Click me
                {% endbird %}
            """,
            expected="<span>Click me</span>",
        )
        test_case.component.create(templates_dir)

        template = Template(
            test_case.template_content,
        )
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Dynamic component name using with",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% with dynamic_name='button' %}
                        {% bird dynamic_name %}
                            Click me
                        {% endbird %}
                    {% endwith %}
                """,
                expected="<button>Click me</button>",
            ),
            TestComponentCase(
                description="Dynamic component name from context",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird dynamic-name %}
                        Click me
                    {% endbird %}
                """,
                template_context={"dynamic-name": "button"},
                expected="<button>Click me</button>",
            ),
            TestComponentCase(
                description="Quoted component name should not be dynamic",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird "button" %}
                        Click me
                    {% endbird %}
                """,
                template_context={"button": "dynamic_name"},
                expected="<button>Click me</button>",
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_dynamic_name_template_context_templatetag(
        self, test_case, templates_dir, normalize_whitespace
    ):
        test_case.component.create(templates_dir)

        template = Template(
            test_case.template_content,
        )
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    def test_dynamic_name_with_string(self, templates_dir, normalize_whitespace):
        button = TestComponent(
            name="button",
            content="""
                <button>
                    {{ slot }}
                </button>
            """,
        )
        not_button = TestComponent(
            name="not_button",
            content="""
                <div>
                    {{ slot }}
                </div>
            """,
        )
        button.create(templates_dir)
        not_button.create(templates_dir)

        template = Template("{% bird 'button' %}Click me{% endbird %}")
        rendered = template.render(Context({"button": "not_button"}))

        assert normalize_whitespace(rendered) == "<button>Click me</button>"
        assert normalize_whitespace(rendered) != "<div>Click me</div>"

    def test_nonexistent_name_templatetag(self, templates_dir):
        template = Template("{% bird nonexistent %}Content{% endbird %}")

        with pytest.raises(TemplateDoesNotExist):
            template.render(Context({}))


def test_self_closing_tag(templates_dir, normalize_whitespace):
    test_case = TestComponentCase(
        component=TestComponent(
            name="image",
            content="<img src='image' />",
        ),
        template_content="{% bird image src='image' / %}",
        expected="<img src='image' />",
    )
    test_case.component.create(templates_dir)

    template = Template(
        test_case.template_content,
    )
    rendered = template.render(Context(test_case.template_context))

    assert normalize_whitespace(rendered) == test_case.expected


class TestAttributes:
    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Renders class attribute",
                component=TestComponent(
                    name="button",
                    content="""
                        <button {{ attrs }}>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class='btn' %}
                        Click me
                    {% endbird %}
                """,
                expected='<button class="btn">Click me</button>',
            ),
            TestComponentCase(
                description="Renders multiple attributes",
                component=TestComponent(
                    name="button",
                    content="""
                        <button {{ attrs }}>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class='btn' id='my-btn' %}
                        Click me
                    {% endbird %}
                """,
                expected='<button class="btn" id="my-btn">Click me</button>',
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_basic(self, test_case, templates_dir, normalize_whitespace):
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Implicit boolean attribute",
                component=TestComponent(
                    name="button",
                    content="""
                        <button {{ attrs }}>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button disabled %}
                        Click me
                    {% endbird %}
                """,
                expected="<button disabled>Click me</button>",
            ),
            TestComponentCase(
                description="Explicit boolean True",
                component=TestComponent(
                    name="button",
                    content="""
                        <button {{ attrs }}>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button disabled=True %}
                        Click me
                    {% endbird %}
                """,
                expected="<button disabled>Click me</button>",
            ),
            TestComponentCase(
                description="Omits boolean False",
                component=TestComponent(
                    name="button",
                    content="""
                        <button {{ attrs }}>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button disabled=False %}
                        Click me
                    {% endbird %}
                """,
                expected="<button>Click me</button>",
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_boolean(self, test_case, templates_dir, normalize_whitespace):
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Dynamic attrs using with",
                component=TestComponent(
                    name="button",
                    content="""
                        <button {{ attrs }}>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% with dynamic_class='btn-primary' %}
                        {% bird button class=dynamic_class %}
                            Click me
                        {% endbird %}
                    {% endwith %}
                """,
                expected='<button class="btn-primary">Click me</button>',
            ),
            TestComponentCase(
                description="Dynamic attrs using template context",
                component=TestComponent(
                    name="button",
                    content="""
                        <button {{ attrs }}>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class=dynamic_class %}
                        Click me
                    {% endbird %}
                """,
                template_context={"dynamic_class": "btn-primary"},
                expected='<button class="btn-primary">Click me</button>',
            ),
            TestComponentCase(
                description="Literal string over context value",
                component=TestComponent(
                    name="button",
                    content="""
                        <button {{ attrs }}>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class='dynamic_class' %}
                        Click me
                    {% endbird %}
                """,
                template_context={"dynamic_class": "btn-primary"},
                expected='<button class="dynamic_class">Click me</button>',
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_dynamic_template_context(
        self, test_case, templates_dir, normalize_whitespace
    ):
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Resolves nested object attribute",
                component=TestComponent(
                    name="button",
                    content="""
                        <button {{ attrs }}>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class=btn.class %}
                        Click me
                    {% endbird %}
                """,
                template_context={
                    "btn": {
                        "class": "btn-success",
                    },
                },
                expected='<button class="btn-success">Click me</button>',
            ),
            TestComponentCase(
                description="Preserves literal nested path",
                component=TestComponent(
                    name="button",
                    content="""
                        <button {{ attrs }}>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class='btn.class' %}
                        Click me
                    {% endbird %}
                """,
                template_context={
                    "btn": {
                        "class": "btn-success",
                    },
                },
                expected='<button class="btn.class">Click me</button>',
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_nested_template_context(
        self, test_case, templates_dir, normalize_whitespace
    ):
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Handles undefined variable",
                component=TestComponent(
                    name="button",
                    content="""
                        <button {{ attrs }}>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class=undefined_class %}
                        Click me
                    {% endbird %}
                """,
                expected='<button class="undefined_class">Click me</button>',
            ),
            TestComponentCase(
                description="Handles missing nested attribute",
                component=TestComponent(
                    name="button",
                    content="""
                        <button {{ attrs }}>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class=missing.attr %}
                        Click me
                    {% endbird %}
                """,
                expected='<button class="missing.attr">Click me</button>',
            ),
            TestComponentCase(
                description="Handles empty nested object",
                component=TestComponent(
                    name="button",
                    content="""
                        <button {{ attrs }}>
                            Click me
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class=user.preferences.theme %}
                        Click me
                    {% endbird %}
                """,
                template_context={
                    "user": {
                        "preferences": {},
                    }
                },
                expected='<button class="user.preferences.theme">Click me</button>',
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_error_handling(self, test_case, templates_dir, normalize_whitespace):
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    @pytest.mark.parametrize(
        "attr_app_setting,expected",
        [
            ({"ENABLE_BIRD_ATTRS": True}, True),
            ({"ENABLE_BIRD_ATTRS": False}, False),
        ],
    )
    def test_data_bird_attributes(
        self,
        attr_app_setting,
        expected,
        override_app_settings,
        templates_dir,
        normalize_whitespace,
    ):
        button = TestComponent(
            name="button",
            content="""
                <button {{ attrs }}>
                    {{ slot }}
                </button>
            """,
        ).create(templates_dir)

        template = Template("{% bird 'button' %}Click me{% endbird %}")

        with override_app_settings(**attr_app_setting):
            rendered = template.render(Context({}))

        comp = Component.from_name(button.name)

        assert (f'data-bird-id="{comp.id}' in rendered) is expected
        assert (f"data-bird-{comp.data_attribute_name}" in rendered) is expected


class TestProperties:
    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Basic prop passing",
                component=TestComponent(
                    name="button",
                    content="""
                        {% bird:prop id %}
                        <button id='{{ props.id }}'>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button id='foo' %}
                        Click me
                    {% endbird %}
                """,
                expected="<button id='foo'>Click me</button>",
            ),
            TestComponentCase(
                description="Default prop value",
                component=TestComponent(
                    name="button",
                    content="""
                        {% bird:prop id='default' %}
                        <button id='{{ props.id }}'>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button %}
                        Click me
                    {% endbird %}
                """,
                expected="<button id='default'>Click me</button>",
            ),
            TestComponentCase(
                description="Override default prop",
                component=TestComponent(
                    name="button",
                    content="""
                        {% bird:prop id='default' %}
                        <button id='{{ props.id }}'>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button id='foo' %}
                        Click me
                    {% endbird %}
                """,
                expected="<button id='foo'>Click me</button>",
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_basic(self, test_case, templates_dir, normalize_whitespace):
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Dynamic props using with",
                component=TestComponent(
                    name="button",
                    content="""
                        {% bird:prop class %}
                        <button class='{{ props.class }}'>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% with dynamic_class='btn-primary' %}
                        {% bird button class=dynamic_class %}
                            Click me
                        {% endbird %}
                    {% endwith %}
                """,
                expected="<button class='btn-primary'>Click me</button>",
            ),
            TestComponentCase(
                description="Dynamic props using template context",
                component=TestComponent(
                    name="button",
                    content="""
                        {% bird:prop class %}
                        <button class='{{ props.class }}'>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class=dynamic_class %}
                        Click me
                    {% endbird %}
                """,
                template_context={
                    "dynamic_class": "btn-primary",
                },
                expected="<button class='btn-primary'>Click me</button>",
            ),
            TestComponentCase(
                description="Literal string over context value",
                component=TestComponent(
                    name="button",
                    content="""
                        {% bird:prop class %}
                        <button class='{{ props.class }}'>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class='dynamic_class' %}
                        Click me
                    {% endbird %}
                """,
                template_context={
                    "dynamic_class": "btn-primary",
                },
                expected="<button class='dynamic_class'>Click me</button>",
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_dynamic(self, test_case, templates_dir, normalize_whitespace):
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Undefined variable",
                component=TestComponent(
                    name="button",
                    content="""
                        {% bird:prop class %}
                        <button class='{{ props.class }}'>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class=undefined_class %}
                        Click me
                    {% endbird %}
                """,
                expected="<button class='undefined_class'>Click me</button>",
            ),
            TestComponentCase(
                description="Missing nested attribute",
                component=TestComponent(
                    name="button",
                    content="""
                        {% bird:prop class %}
                        <button class='{{ props.class }}'>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class=missing.attr %}
                        Click me
                    {% endbird %}
                """,
                expected="<button class='missing.attr'>Click me</button>",
            ),
            TestComponentCase(
                description="Empty nested object",
                component=TestComponent(
                    name="button",
                    content="""
                        {% bird:prop class %}
                        <button class='{{ props.class }}'>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class=user.preferences.theme %}
                        Click me
                    {% endbird %}
                """,
                template_context={"user": {"preferences": {}}},
                expected="<button class='user.preferences.theme'>Click me</button>",
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_error_handling(self, test_case, templates_dir, normalize_whitespace):
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected


def test_attrs_and_props(templates_dir, normalize_whitespace):
    test_case = TestComponentCase(
        component=TestComponent(
            name="button",
            content="""
                    {% bird:prop id="default" %}
                    {% bird:prop class="btn" %}

                    <button id="{{ props.id }}" class="{{ props.class }}" {{ attrs }}>
                        {{ slot }}
                    </button>
                """,
        ),
        template_content="""
            {% bird button data-test='value' %}
                Click me
            {% endbird %}
        """,
        expected='<button id="default" class="btn" data-test="value">Click me</button>',
    )
    test_case.component.create(templates_dir)

    template = Template(test_case.template_content)
    rendered = template.render(Context(test_case.template_context))

    assert normalize_whitespace(rendered) == test_case.expected


class TestSlots:
    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Default slot renders content",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button %}
                        Click me
                    {% endbird %}
                """,
                expected="<button>Click me</button>",
            ),
            TestComponentCase(
                description="Empty named slot declaration",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            {% bird:slot %}{% endbird:slot %}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button %}
                        Click me
                    {% endbird %}
                """,
                expected="<button>Click me</button>",
            ),
            TestComponentCase(
                description="Named default slot",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            {% bird:slot default %}{% endbird:slot %}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button %}
                        Click me
                    {% endbird %}
                """,
                expected="<button>Click me</button>",
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_default(self, test_case, templates_dir, normalize_whitespace):
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Renders content in named slot alongside default slot",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            <span>
                                {% bird:slot leading-icon %}{% endbird:slot %}
                            </span>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button %}
                        {% bird:slot leading-icon %}
                            Icon here
                        {% endbird:slot %}
                        Click me
                    {% endbird %}
                """,
                expected="<button><span>Icon here</span>Click me</button>",
            ),
            TestComponentCase(
                description="Renders multiple named slots in different positions",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            {% bird:slot prefix %}{% endbird:slot %}
                            <span>{{ slot }}</span>
                            {% bird:slot suffix %}{% endbird:slot %}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button %}
                        {% bird:slot prefix %}Before{% endbird:slot %}
                        Click me
                        {% bird:slot suffix %}After{% endbird:slot %}
                    {% endbird %}
                """,
                expected="<button>Before<span>Click me</span>After</button>",
            ),
            TestComponentCase(
                description="Renders named slots with component variables",
                component=TestComponent(
                    name="button",
                    content="""
                        <button {{ attrs }}>
                            {% bird:slot prefix %}{% endbird:slot %}
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button class="primary" %}
                        {% bird:slot prefix %}→{% endbird:slot %}
                        Submit
                    {% endbird %}
                """,
                expected='<button class="primary">→ Submit</button>',
            ),
            TestComponentCase(
                description="Handles empty named slots by rendering nothing",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            {% bird:slot prefix %}{% endbird:slot %}
                            {{ slot }}
                            {% bird:slot suffix %}{% endbird:slot %}
                        </button>
                    """,
                ),
                template_content="""
                    {% bird button %}
                        Click me
                    {% endbird %}
                """,
                expected="<button>Click me</button>",
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_named(self, test_case, templates_dir, normalize_whitespace):
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected

    @pytest.fixture
    def fancy_filter(self):
        register = Library()

        @register.filter
        def make_fancy(value):
            return f"✨{value}✨"

        engine = Engine.get_default()
        engine.template_libraries["custom_filters"] = register

        yield

        del engine.template_libraries["custom_filters"]

    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Filter in default slot",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% load custom_filters %}
                    {% bird button %}
                        {{ text|make_fancy }}
                    {% endbird %}
                """,
                template_context={"text": "click me"},
                expected="<button>✨click me✨</button>",
            ),
            TestComponentCase(
                description="Filter in named slot",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            {% bird:slot label %}{% endbird:slot %}
                        </button>
                    """,
                ),
                template_content="""
                    {% load custom_filters %}
                    {% bird button %}
                        {% bird:slot label %}
                            {{ text|make_fancy }}
                        {% endbird:slot %}
                    {% endbird %}
                """,
                template_context={"text": "click me"},
                expected="<button>✨click me✨</button>",
            ),
            TestComponentCase(
                description="Filters in multiple slots",
                component=TestComponent(
                    name="button",
                    content="""
                        <button>
                            <span>
                                {% bird:slot icon %}{% endbird:slot %}
                            </span>
                            {{ slot }}
                        </button>
                    """,
                ),
                template_content="""
                    {% load custom_filters %}
                    {% bird button %}
                        {% bird:slot icon %}
                            {{ icon_text|make_fancy }}
                        {% endbird:slot %}
                        {{ text|make_fancy }}
                    {% endbird %}
                """,
                template_context={"text": "click me", "icon_text": "icon"},
                expected="<button><span>✨icon✨</span>✨click me✨</button>",
            ),
        ],
        ids=lambda x: x.description,
    )
    def test_with_outside_templatetag(
        self, test_case, fancy_filter, templates_dir, normalize_whitespace
    ):
        test_case.component.create(templates_dir)

        template = Template(test_case.template_content)
        rendered = template.render(Context(test_case.template_context))

        assert normalize_whitespace(rendered) == test_case.expected


def test_nested_components_with_loops(templates_dir, normalize_whitespace):
    nav = TestComponent(
        name="nav",
        content="""
            <nav>
                {{ slot }}
            </nav>
        """,
    )
    nav.create(templates_dir)

    nav_item = TestComponent(
        name="item",
        content="""
            {% bird:prop href="#" %}

            <a href="{{ props.href }}">{{ slot }}</a>
        """,
        sub_dir="nav",
    )
    nav_item.create(templates_dir)

    template = Template("""
        {% bird nav %}
            {% for item in items %}
                {% bird nav.item href=item.url %}
                    {{ item.title }}
                {% endbird nav.item %}
            {% endfor %}
        {% endbird nav %}
    """)

    context = Context(
        {
            "items": [
                {"url": "/", "title": "Home"},
                {"url": "/admin", "title": "Admin"},
            ]
        }
    )

    rendered = template.render(context)

    assert normalize_whitespace(rendered) == normalize_whitespace("""
        <nav>
            <a href="/">Home</a>
            <a href="/admin">Admin</a>
        </nav>
    """)


@pytest.mark.parametrize(
    "test_case",
    [
        TestComponentCase(
            description="Access parent context variable",
            component=TestComponent(
                name="button",
                content="""
                    <button>
                        {{ user.name }}
                    </button>
                """,
            ),
            template_content="""
                {% bird button %}{% endbird %}
            """,
            template_context={"user": {"name": "John"}},
            expected="<button>John</button>",
        ),
        TestComponentCase(
            description="Access parent context in slot",
            component=TestComponent(
                name="button",
                content="""
                    <button>
                        {{ slot }}
                    </button>
                """,
            ),
            template_content="""
                {% bird button %}
                    {{ user.name }}
                {% endbird %}
            """,
            template_context={"user": {"name": "John"}},
            expected="<button>John</button>",
        ),
        TestComponentCase(
            description="Access parent context in named slot",
            component=TestComponent(
                name="button",
                content="""
                    <button>
                        {% bird:slot prefix %}{% endbird:slot %}
                        {{ slot }}
                    </button>
                """,
            ),
            template_content="""
                {% bird button %}
                    {% bird:slot prefix %}{{ user.role }}{% endbird:slot %}
                    {{ user.name }}
                {% endbird %}
            """,
            template_context={"user": {"name": "John", "role": "Admin"}},
            expected="<button>Admin John</button>",
        ),
        TestComponentCase(
            description="Component-specific context overrides parent context values",
            component=TestComponent(
                name="button",
                content="""
                    <button {{ attrs }}>
                        {{ slot }}
                    </button>
                """,
            ),
            template_content="""
                {% bird button id="foo" %}
                    Component Content
                {% endbird %}
            """,
            template_context={
                "slot": "Parent Content",
                "attrs": 'id="bar"',
            },
            expected='<button id="foo">Component Content</button>',
        ),
    ],
    ids=lambda x: x.description,
)
def test_parent_context_access(test_case, templates_dir, normalize_whitespace):
    test_case.component.create(templates_dir)

    template = Template(test_case.template_content)
    rendered = template.render(Context(test_case.template_context))

    assert normalize_whitespace(rendered) == test_case.expected


@pytest.mark.parametrize(
    "test_case",
    [
        TestComponentCase(
            description="Only flag prevents access to parent context",
            component=TestComponent(
                name="button",
                content="""
                    <button>
                        {{ user.name|default:"Anonymous" }}
                    </button>
                """,
            ),
            template_content="""
                {% bird button only %}{% endbird %}
            """,
            template_context={"user": {"name": "John"}},
            expected="<button>Anonymous</button>",
        ),
        TestComponentCase(
            description="Only flag still allows props and slots",
            component=TestComponent(
                name="button",
                content="""
                    {% bird:prop label %}
                    <button {{ attrs }}>
                        {{ props.label }}
                        {{ slot }}
                        {{ user.name|default:"Anonymous" }}
                    </button>
                """,
            ),
            template_content="""
                {% bird button id="foo" label="Click" only %}
                    Content
                {% endbird %}
            """,
            template_context={
                "props": {
                    "label": "Outside",
                },
                "user": {"name": "John"},
            },
            expected='<button id="foo">Click Content Anonymous</button>',
        ),
        TestComponentCase(
            description="Only flag with named slots",
            component=TestComponent(
                name="button",
                content="""
                    <button>
                        {% bird:slot prefix %}{% endbird:slot %}
                        {{ user.name|default:"Anonymous" }}
                    </button>
                """,
            ),
            template_content="""
                {% bird button only %}
                    {% bird:slot prefix %}{{ user.role|default:"User" }}{% endbird:slot %}
                {% endbird %}
            """,
            template_context={"user": {"name": "John", "role": "Admin"}},
            expected="<button>User Anonymous</button>",
        ),
        TestComponentCase(
            description="Only flag with self-closing tag",
            component=TestComponent(
                name="button",
                content="""
                    <button>
                        {{ user.name|default:"Anonymous" }}
                    </button>
                """,
            ),
            template_content="""
                {% bird button only / %}
            """,
            template_context={"user": {"name": "John"}},
            expected="<button>Anonymous</button>",
        ),
    ],
    ids=lambda x: x.description,
)
def test_only_flag(test_case, templates_dir, normalize_whitespace):
    test_case.component.create(templates_dir)

    template = Template(test_case.template_content)
    rendered = template.render(Context(test_case.template_context))

    assert normalize_whitespace(rendered) == test_case.expected


class TestBirdNode:
    @pytest.mark.parametrize(
        "test_case",
        [
            TestComponentCase(
                description="Static name",
                component=TestComponent(
                    name="button",
                    content="",
                ),
                template_content="",
                expected="button",
            ),
            TestComponentCase(
                description="Dynamic name",
                component=TestComponent(
                    name="button",
                    content="",
                ),
                template_content="",
                template_context={
                    "dynamic-name": "button",
                },
                expected="button",
            ),
        ],
    )
    def test_get_component_name(self, test_case, templates_dir):
        test_case.component.create(templates_dir)

        node = BirdNode(name=test_case.component.name, attrs=[], nodelist=None)

        component_name = node.get_component_name(
            context=Context(test_case.template_context)
        )

        assert component_name == test_case.expected
