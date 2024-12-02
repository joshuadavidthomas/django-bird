from __future__ import annotations

from unittest.mock import patch

import pytest
from django.template import Context
from django.template import Library
from django.template import Template
from django.template.base import Parser
from django.template.base import Token
from django.template.base import TokenType
from django.template.exceptions import TemplateSyntaxError

from django_bird.components.params import Param
from django_bird.components.params import Params
from django_bird.templatetags.tags.bird import END_TAG
from django_bird.templatetags.tags.bird import TAG
from django_bird.templatetags.tags.bird import BirdNode
from django_bird.templatetags.tags.bird import do_bird


class TestTemplateTag:
    @pytest.mark.parametrize(
        "name,expected",
        [
            ("button", "button"),
            ("'button'", "button"),
            ('"button"', "button"),
            ("button.label", "button.label"),
        ],
    )
    def test_node_name(self, name, expected):
        token = Token(TokenType.BLOCK, f"{TAG} {name}")
        parser = Parser(
            [Token(TokenType.BLOCK, END_TAG)],
        )
        node = do_bird(parser, token)
        assert node.name == expected

    def test_missing_argument(self):
        token = Token(TokenType.BLOCK, TAG)
        parser = Parser(
            [Token(TokenType.BLOCK, END_TAG)],
        )
        with pytest.raises(TemplateSyntaxError):
            do_bird(parser, token)

    @pytest.mark.parametrize(
        "params,expected_params",
        [
            ("class='btn'", Params(attrs=[Param(name="class", value="btn")])),
            (
                "class='btn' id='my-btn'",
                Params(
                    attrs=[
                        Param(name="class", value="btn"),
                        Param(name="id", value="my-btn"),
                    ]
                ),
            ),
            ("disabled", Params(attrs=[Param(name="disabled", value=True)])),
        ],
    )
    def test_node_params(self, params, expected_params):
        token = Token(TokenType.BLOCK, f"{TAG} button {params}")
        parser = Parser(
            [Token(TokenType.BLOCK, END_TAG)],
        )
        node = do_bird(parser, token)
        assert node.params == expected_params

    @pytest.mark.parametrize(
        "component,template,context,expected",
        [
            (
                "<button>Click me</button>",
                "{% bird button %}Click me{% endbird %}",
                {},
                "<button>Click me</button>",
            ),
            (
                "<button>Click me</button>",
                "{% bird 'button' %}Click me{% endbird %}",
                {},
                "<button>Click me</button>",
            ),
            (
                "<button>Click me</button>",
                '{% bird "button" %}Click me{% endbird %}',
                {},
                "<button>Click me</button>",
            ),
            (
                "<button>Click me</button>",
                "{% with dynamic_name='button' %}{% bird dynamic_name %}Click me{% endbird %}{% endwith %}",
                {},
                "<button>Click me</button>",
            ),
            (
                "<button>Click me</button>",
                "{% bird dynamic-name %}Click me{% endbird %}",
                {"dynamic-name": "button"},
                "<button>Click me</button>",
            ),
        ],
    )
    def test_rendered_name(
        self,
        component,
        template,
        context,
        expected,
        create_bird_template,
        normalize_whitespace,
    ):
        create_bird_template("button", component)
        t = Template(template)
        rendered = t.render(context=Context(context))
        assert normalize_whitespace(rendered) == expected

    @pytest.mark.parametrize(
        "component,template,context,expected",
        [
            (
                "<button {{ attrs }}>Click me</button>",
                "{% bird button class='btn' %}Click me{% endbird %}",
                {},
                '<button class="btn">Click me</button>',
            ),
            (
                "<button {{ attrs }}>Click me</button>",
                "{% bird button class='btn' id='my-btn' disabled %}Click me{% endbird %}",
                {},
                '<button class="btn" id="my-btn" disabled>Click me</button>',
            ),
            (
                "<button {{ attrs }}>{{ slot }}</button>",
                "{% bird button %}{{ slot }}{% endbird %}",
                {"slot": "Click me"},
                "<button>Click me</button>",
            ),
        ],
    )
    def test_rendered_attrs(
        self,
        component,
        template,
        context,
        expected,
        create_bird_template,
        normalize_whitespace,
    ):
        create_bird_template("button", component)
        t = Template(template)
        rendered = t.render(context=Context(context))
        assert normalize_whitespace(rendered) == expected

    def test_self_closing_tag(self, create_bird_template):
        create_bird_template(name="image", content="<img src='image' />")
        template = Template("{% bird image src='image' / %}")
        rendered = template.render(context=Context({}))
        assert rendered == "<img src='image' />"

    @pytest.mark.parametrize(
        "component,template,context,expected",
        [
            (
                "<button>{{ slot }}</button>",
                "{% bird button %}Click me{% endbird %}",
                {},
                "<button>Click me</button>",
            ),
            (
                "<button>{% bird:slot %}{% endbird:slot %}</button>",
                "{% bird button %}Click me{% endbird %}",
                {},
                "<button>Click me</button>",
            ),
            (
                "<button>{% bird:slot default %}{% endbird:slot %}</button>",
                "{% bird button %}Click me{% endbird %}",
                {},
                "<button>Click me</button>",
            ),
            (
                "<button><span>{% bird:slot leading-icon %}{% endbird:slot %}</span>{{ slot }}</button>",
                "{% bird button %}{% bird:slot leading-icon %}Icon here{% endbird:slot %}Click me{% endbird %}",
                {},
                "<button><span>Icon here</span>Click me</button>",
            ),
        ],
    )
    def test_with_slots(
        self,
        component,
        template,
        context,
        expected,
        create_bird_template,
        normalize_whitespace,
    ):
        create_bird_template("button", component)
        t = Template(template)
        rendered = t.render(context=Context(context))
        assert normalize_whitespace(rendered) == expected

    @pytest.mark.parametrize(
        "component,template,context,expected",
        [
            (
                "<button>{{ slot }}</button>",
                "{% load custom_filters %}{% bird button %}{{ text|make_fancy }}{% endbird %}",
                {"text": "click me"},
                "<button>✨click me✨</button>",
            ),
            (
                "<button>{% bird:slot label %}{% endbird:slot %}</button>",
                "{% load custom_filters %}{% bird button %}{% bird:slot label %}{{ text|make_fancy }}{% endbird:slot %}{% endbird %}",
                {"text": "click me"},
                "<button>✨click me✨</button>",
            ),
            (
                "<button><span>{% bird:slot icon %}{% endbird:slot %}</span>{{ slot }}</button>",
                "{% load custom_filters %}{% bird button %}{% bird:slot icon %}{{ icon_text|make_fancy }}{% endbird:slot %}{{ text|make_fancy }}{% endbird %}",
                {"text": "click me", "icon_text": "icon"},
                "<button><span>✨icon✨</span>✨click me✨</button>",
            ),
        ],
    )
    def test_slots_with_outside_templatetag(
        self,
        component,
        template,
        context,
        expected,
        create_bird_template,
        normalize_whitespace,
    ):
        register = Library()

        @register.filter
        def make_fancy(value):
            return f"✨{value}✨"

        def get_template_libraries(self, libraries):
            return {"custom_filters": register}

        with patch(
            "django.template.engine.Engine.get_template_libraries",
            get_template_libraries,
        ):
            create_bird_template("button", component)
            t = Template(template)
            rendered = t.render(context=Context(context))
            assert normalize_whitespace(rendered) == expected

    @pytest.mark.parametrize(
        "component,template,context,expected",
        [
            (
                "{% bird:prop id %}<button id='{{ props.id }}'>{{ slot }}</button>",
                "{% bird button id='foo' %}Click me{% endbird %}",
                {},
                "<button id='foo'>Click me</button>",
            ),
            (
                "{% bird:prop id='default' %}<button id='{{ props.id }}'>{{ slot }}</button>",
                "{% bird button %}Click me{% endbird %}",
                {},
                "<button id='default'>Click me</button>",
            ),
            (
                "{% bird:prop id='default' %}<button id='{{ props.id }}'>{{ slot }}</button>",
                "{% bird button id='foo' %}Click me{% endbird %}",
                {},
                "<button id='foo'>Click me</button>",
            ),
        ],
    )
    def test_with_props(
        self,
        component,
        template,
        context,
        expected,
        create_bird_template,
        normalize_whitespace,
    ):
        create_bird_template("button", component)
        t = Template(template)
        rendered = t.render(context=Context(context))
        assert normalize_whitespace(rendered) == expected


@pytest.mark.xfail(reason="Feature not implemented yet")
class TestTemplateTagFutureFeatures:
    def test_dynamic_attrs(self, create_bird_template):
        create_bird_template(
            name="button", content="<button class=btn_class>Click me</button>"
        )
        template = Template("{% bird button class=btn_class %}Click me{% endbird %}")
        rendered = template.render(context=Context({"btn_class": "primary"}))
        assert rendered == "<button class='primary'>Click me</button>"


class TestNode:
    @pytest.mark.parametrize(
        "name,context,expected",
        [
            (
                "button",
                {},
                "button",
            ),
            (
                "dynamic-name",
                {"dynamic-name": "button"},
                "button",
            ),
        ],
    )
    def test_get_component_name(self, name, context, expected, create_bird_template):
        create_bird_template(name=name, content="<button>Click me</button>")
        node = BirdNode(name=name, params=Params([]), nodelist=None)

        component_name = node.get_component_name(context=Context(context))

        assert component_name == expected
