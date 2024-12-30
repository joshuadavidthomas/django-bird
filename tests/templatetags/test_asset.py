from __future__ import annotations

import pytest
from django.template.base import Parser
from django.template.base import Token
from django.template.base import TokenType
from django.template.context import Context
from django.template.exceptions import TemplateSyntaxError

from django_bird.staticfiles import AssetType
from django_bird.templatetags.tags.asset import CSS_TAG
from django_bird.templatetags.tags.asset import JS_TAG
from django_bird.templatetags.tags.asset import AssetNode
from django_bird.templatetags.tags.asset import do_asset


class TestTemplateTag:
    @pytest.mark.parametrize(
        "tag,expected",
        [
            (CSS_TAG, AssetType.CSS),
            (JS_TAG, AssetType.JS),
        ],
    )
    def test_asset_type(self, tag, expected):
        token = Token(TokenType.BLOCK, tag)
        parser = Parser([])
        node = do_asset(parser, token)
        assert node.asset_type == expected

    def test_missing_tag_name(self):
        token = Token(TokenType.BLOCK, "")
        parser = Parser([])
        with pytest.raises(TemplateSyntaxError):
            do_asset(parser, token)

    @pytest.mark.parametrize(
        "tag",
        ["bird:jsx", "birdcss"],
    )
    def test_invalid_tag_name(self, tag):
        token = Token(TokenType.BLOCK, tag)
        parser = Parser([])
        with pytest.raises(ValueError):
            do_asset(parser, token)

    def test_template_inheritence(
        self, create_bird_template, create_bird_asset, create_template, templates_dir
    ):
        alert = create_bird_template("alert", '<div class="alert">{{ slot }}</div>')
        alert_css = create_bird_asset(alert, ".alert { color: red; }", "css")
        alert_js = create_bird_asset(alert, "console.log('alert');", "js")

        button = create_bird_template("button", "<button>{{ slot }}</button>")
        button_css = create_bird_asset(button, ".button { color: blue; }", "css")
        button_js = create_bird_asset(button, "console.log('button');", "js")

        base_path = templates_dir / "base.html"
        base_path.write_text("""
            <html>
            <head>
                <title>Test</title>
                {% bird:css %}
            </head>
            <body>
                {% bird alert %}Base Alert{% endbird %}
                {% block content %}{% endblock %}
                {% bird:js %}
            </body>
            </html>
        """)

        child_path = templates_dir / "child.html"
        child_path.write_text("""
            {% extends 'base.html' %}
            {% block content %}
                {% bird button %}Click me{% endbird %}
            {% endblock %}
        """)

        template = create_template(child_path)

        rendered = template.render({})

        assert f'<link rel="stylesheet" href="{alert_css}">' in rendered
        assert f'<link rel="stylesheet" href="{button_css}">' in rendered
        assert f'<script src="{alert_js}"></script>' in rendered
        assert f'<script src="{button_js}"></script>' in rendered

    def test_with_no_assets(
        self, create_bird_template, create_bird_asset, create_template, templates_dir
    ):
        create_bird_template("alert", '<div class="alert">{{ slot }}</div>')

        base_path = templates_dir / "base.html"
        base_path.write_text("""
            <html>
            <head>
                <title>Test</title>
                {% bird:css %}
            </head>
            <body>
                {% bird alert %}Base Alert{% endbird %}
                {% block content %}{% endblock %}
                {% bird:js %}
            </body>
            </html>
        """)

        template = create_template(base_path)

        rendered = template.render({})

        assert '<link rel="stylesheet" href="' not in rendered
        assert '<script src="' not in rendered

    def test_component_render_order(
        self, create_bird_template, create_bird_asset, create_template, templates_dir
    ):
        first = create_bird_template("first", "<div>First: {{ slot }}</div>")
        first_css = create_bird_asset(first, ".first { color: red; }", "css")
        first_js = create_bird_asset(first, "console.log('first');", "js")

        second = create_bird_template("second", "<div>Second: {{ slot }}</div>")
        second_css = create_bird_asset(second, ".second { color: red; }", "css")
        second_js = create_bird_asset(second, "console.log('second');", "js")

        template_path = templates_dir / "test.html"
        template_path.write_text("""
            <html>
            <head>
                {% bird:css %}
            </head>
            <body>
                <div>
                    {% bird first %}One{% endbird %}
                    <p>Some content</p>
                    {% bird second %}Two{% endbird %}
                </div>
                {% bird:js %}
            </body>
            </html>
        """)

        template = create_template(template_path)

        rendered = template.render({})

        head_end = rendered.find("</head>")
        assert f'<link rel="stylesheet" href="{first_css}">' in rendered[:head_end]
        assert f'<link rel="stylesheet" href="{second_css}">' in rendered[:head_end]

        body_start = rendered.find("<body")
        assert f'<script src="{first_js}"></script>' in rendered[body_start:]
        assert f'<script src="{second_js}"></script>' in rendered[body_start:]


class TestNode:
    def test_no_template(self):
        node = AssetNode(AssetType.CSS)
        context = Context({})
        assert node.render(context) == ""
