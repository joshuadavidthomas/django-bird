from __future__ import annotations

import pytest
from django.template import Context
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
                "<button class='btn'>Click me</button>",
                "{% bird button class='btn' %}Click me{% endbird %}",
                {},
                "<button class='btn'>Click me</button>",
            ),
            (
                "<button class='btn' id='my-btn' disabled>Click me</button>",
                "{% bird button class='btn' id='my-btn' disabled %}Click me{% endbird %}",
                {},
                "<button class='btn' id='my-btn' disabled>Click me</button>",
            ),
            (
                "<button>{{ slot }}</button>",
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
            ("{% slot %}{% endslot %}", {"slot": "test"}, "test"),
            ("{% slot default %}{% endslot %}", {"slot": "test"}, "test"),
            ("{% slot 'default' %}{% endslot %}", {"slot": "test"}, "test"),
            ('{% slot "default" %}{% endslot %}', {"slot": "test"}, "test"),
            ("{% slot name='default' %}{% endslot %}", {"slot": "test"}, "test"),
            ('{% slot name="default" %}{% endslot %}', {"slot": "test"}, "test"),
            ("{% slot name='not-default' %}{% endslot %}", {"slot": "test"}, ""),
            (
                "{% slot outer %}Outer {% slot inner %}Inner{% endslot %} Content{% endslot %}",
                {"slots": {"outer": "Replaced Content"}},
                "Replaced Content",
            ),
            (
                "{% slot outer %}Outer {% slot inner %}Inner{% endslot %} Content{% endslot %}",
                {"slots": {"inner": "Replaced Content"}},
                "Outer Replaced Content Content",
            ),
            (
                "{% slot outer %}Outer {% slot inner %}Inner Default{% endslot %} Content{% endslot %}",
                {
                    "slots": {
                        "outer": "Replaced {% slot inner %}{% endslot %} Outer",
                        "inner": "Replaced Inner",
                    },
                },
                "Replaced Replaced Inner Outer",
            ),
            (
                "{{ slot }}",
                {
                    "slot": "Replaced {% slot inner %}{% endslot %} Outer",
                    "slots": {
                        "inner": "Replaced Inner",
                    },
                },
                "Replaced Replaced Inner Outer",
            ),
            (
                "{% slot %}{% endslot %}",
                {},
                "",
            ),
            (
                "{% slot %}Default content{% endslot %}",
                {},
                "Default content",
            ),
            (
                "{% slot 'mal formed' %}{% endslot %}",
                {"slots": {"mal formed": "content"}},
                "content",
            ),
            (
                "{% slot CaseSensitive %}{% endslot %}",
                {"slots": {"CaseSensitive": "Upper", "casesensitive": "Lower"}},
                "Upper",
            ),
            (
                "{% slot %}{% endslot %}",
                {"slots": {"default": 42}},
                "42",
            ),
            (
                "{% slot %}{% endslot %}",
                {"slots": {"default": "<b>Bold</b>"}},
                "<b>Bold</b>",
            ),
            (
                "{% slot unicode_slot %}{% endslot %}",
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
            Template("{% slot too many args %}{% endslot %}")
