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
from django.test import override_settings

from django_bird.templatetags.django_bird import BirdNode
from django_bird.templatetags.django_bird import do_bird
from django_bird.templatetags.django_bird import parse_slot_name


class TestBirdTemplateTag:
    @pytest.mark.parametrize(
        "name_arg,expected",
        [
            ("button", "button"),
            ("'button'", "button"),
            ('"button"', "button"),
            ("button.label", "button.label"),
        ],
    )
    def test_node_name(self, name_arg, expected):
        token = Token(TokenType.BLOCK, f"bird {name_arg}")
        parser = Parser(
            [Token(TokenType.BLOCK, "endbird")],
        )
        node = do_bird(parser, token)
        assert node.name == expected

    def test_missing_argument(self):
        token = Token(TokenType.BLOCK, "bird")
        parser = Parser(
            [Token(TokenType.BLOCK, "endbird")],
        )
        with pytest.raises(TemplateSyntaxError):
            do_bird(parser, token)

    @pytest.mark.parametrize(
        "attrs,expected_attrs",
        [
            ("class='btn'", ["class='btn'"]),
            ("class='btn' id='my-btn'", ["class='btn'", "id='my-btn'"]),
            ("disabled", ["disabled"]),
        ],
    )
    def test_node_attrs(self, attrs, expected_attrs):
        token = Token(TokenType.BLOCK, f"bird button {attrs}")
        parser = Parser(
            [Token(TokenType.BLOCK, "endbird")],
        )
        node = do_bird(parser, token)
        assert node.attrs == expected_attrs

    @pytest.mark.parametrize(
        "component,template,expected",
        [
            (
                "<button>Click me</button>",
                "{% bird button %}Click me{% endbird %}",
                "<button>Click me</button>",
            ),
            (
                "<button>Click me</button>",
                "{% bird 'button' %}Click me{% endbird %}",
                "<button>Click me</button>",
            ),
            (
                "<button>Click me</button>",
                '{% bird "button" %}Click me{% endbird %}',
                "<button>Click me</button>",
            ),
        ],
    )
    def test_rendered_name(
        self, component, template, expected, create_bird_template, normalize_whitespace
    ):
        create_bird_template("button", component)
        t = Template(template)
        rendered = t.render(context=Context({}))
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


@pytest.mark.xfail(reason="Feature not implemented yet")
class TestBirdTemplateTagFutureFeatures:
    def test_dynamic_attrs(self, create_bird_template):
        create_bird_template(
            name="button", content="<button class=btn_class>Click me</button>"
        )
        template = Template("{% bird button class=btn_class %}Click me{% endbird %}")
        rendered = template.render(context=Context({"btn_class": "primary"}))
        assert rendered == "<button class='primary'>Click me</button>"


class TestBirdNode:
    @pytest.mark.parametrize(
        "sub_dir,filename,component,nodename,expected",
        [
            (
                None,
                "button",
                "<button>Click me</button>",
                "button",
                "bird/button.html",
            ),
            (
                "button",
                "index",
                "<button>Click me</button>",
                "button",
                "bird/button/index.html",
            ),
            (
                "button",
                "button",
                "<button>Click me</button>",
                "button",
                "bird/button/button.html",
            ),
            (
                None,
                "button.label",
                "<button>Click me</button>",
                "button.label",
                "bird/button.label.html",
            ),
            (
                None,
                "button.label",
                "<button>Click me</button>",
                "button.label",
                "bird/button/label.html",
            ),
        ],
    )
    def test_get_template_names(
        self, sub_dir, filename, component, nodename, expected, create_bird_template
    ):
        create_bird_template(name=filename, content=component, sub_dir=sub_dir)
        node = BirdNode(name=nodename, attrs=[], nodelist=None)

        template_names = node.get_template_names()

        assert any(expected in template_name for template_name in template_names)

    @override_settings(DJANGO_BIRD={"COMPONENT_DIRS": ["not_default"]})
    def test_get_template_names_path_component_dirs(self, create_bird_template):
        create_bird_template(
            name="button",
            content="<button class=btn_class>Click me</button>",
            bird_dir_name="not_default",
        )

        node = BirdNode(name="button", attrs=[], nodelist=None)

        template_names = node.get_template_names()

        assert any("not_default" in template_name for template_name in template_names)


class TestSlotsTemplateTag:
    @pytest.mark.parametrize(
        "tag_args,expected",
        [
            (["slot"], "default"),
            (["slot", "foo"], "foo"),
            (["slot", "'foo'"], "foo"),
            (["slot", '"foo"'], "foo"),
            (["slot", 'name="foo"'], "foo"),
            (["slot", "name='foo'"], "foo"),
        ],
    )
    def test_parse_slot_name(self, tag_args, expected):
        assert parse_slot_name(tag_args) == expected

    def test_parse_slot_name_no_args(self):
        with pytest.raises(TemplateSyntaxError):
            assert parse_slot_name([])

    @pytest.mark.parametrize(
        "template,context,expected",
        [
            ("{{ slot }}", {"slot": "test"}, "test"),
            ("{% bird:slot %}{% endbird:slot %}", {"slot": "test"}, "test"),
            ("{% bird:slot default %}{% endbird:slot %}", {"slot": "test"}, "test"),
            ("{% bird:slot 'default' %}{% endbird:slot %}", {"slot": "test"}, "test"),
            ('{% bird:slot "default" %}{% endbird:slot %}', {"slot": "test"}, "test"),
            (
                "{% bird:slot name='default' %}{% endbird:slot %}",
                {"slot": "test"},
                "test",
            ),
            (
                '{% bird:slot name="default" %}{% endbird:slot %}',
                {"slot": "test"},
                "test",
            ),
            (
                "{% bird:slot name='not-default' %}{% endbird:slot %}",
                {"slot": "test"},
                "",
            ),
            (
                "{% bird:slot outer %}Outer {% bird:slot inner %}Inner{% endbird:slot %} Content{% endbird:slot %}",
                {"slots": {"outer": "Replaced Content"}},
                "Replaced Content",
            ),
            (
                "{% bird:slot outer %}Outer {% bird:slot inner %}Inner{% endbird:slot %} Content{% endbird:slot %}",
                {"slots": {"inner": "Replaced Content"}},
                "Outer Replaced Content Content",
            ),
            (
                "{% bird:slot outer %}Outer {% bird:slot inner %}Inner Default{% endbird:slot %} Content{% endbird:slot %}",
                {
                    "slots": {
                        "outer": "Replaced {% bird:slot inner %}{% endbird:slot %} Outer",
                        "inner": "Replaced Inner",
                    },
                },
                "Replaced Replaced Inner Outer",
            ),
            (
                "{{ slot }}",
                {
                    "slot": "Replaced {% bird:slot inner %}{% endbird:slot %} Outer",
                    "slots": {
                        "inner": "Replaced Inner",
                    },
                },
                "Replaced Replaced Inner Outer",
            ),
            (
                "{% bird:slot %}{% endbird:slot %}",
                {},
                "",
            ),
            (
                "{% bird:slot %}Default content{% endbird:slot %}",
                {},
                "Default content",
            ),
            (
                "{% bird:slot 'mal formed' %}{% endbird:slot %}",
                {"slots": {"mal formed": "content"}},
                "content",
            ),
            (
                "{% bird:slot CaseSensitive %}{% endbird:slot %}",
                {"slots": {"CaseSensitive": "Upper", "casesensitive": "Lower"}},
                "Upper",
            ),
            (
                "{% bird:slot %}{% endbird:slot %}",
                {"slots": {"default": 42}},
                "42",
            ),
            (
                "{% bird:slot %}{% endbird:slot %}",
                {"slots": {"default": "<b>Bold</b>"}},
                "<b>Bold</b>",
            ),
            (
                "{% bird:slot unicode_slot %}{% endbird:slot %}",
                {"slots": {"unicode_slot": "こんにちは"}},
                "こんにちは",
            ),
        ],
    )
    def test_rendering(self, template, context, expected, create_bird_template):
        create_bird_template("test", template)
        t = Template(f"{{% bird test %}}{template}{{% endbird %}}")
        rendered = t.render(context=Context(context))
        assert rendered == expected

    def test_too_many_args(self):
        with pytest.raises(TemplateSyntaxError):
            Template("{% bird:slot too many args %}{% endbird:slot %}")
