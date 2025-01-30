from __future__ import annotations

import pytest
from django.conf import settings
from django.template.base import Parser
from django.template.base import Token
from django.template.base import TokenType
from django.template.context import Context
from django.template.exceptions import TemplateSyntaxError
from django.template.loader import get_template
from django.test import override_settings

from django_bird.conf import DJANGO_BIRD_FINDER
from django_bird.staticfiles import AssetType
from django_bird.templatetags.tags.asset import CSS_TAG
from django_bird.templatetags.tags.asset import JS_TAG
from django_bird.templatetags.tags.asset import AssetNode
from django_bird.templatetags.tags.asset import do_asset
from tests.utils import TestAsset
from tests.utils import TestComponent


@pytest.fixture(autouse=True)
def reset_staticfiles_finders():
    with override_settings(
        STATICFILES_FINDERS=[
            finder
            for finder in settings.STATICFILES_FINDERS
            if finder != DJANGO_BIRD_FINDER
        ]
    ):
        yield


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

    def test_template_inheritence(self, create_template, templates_dir, registry):
        alert = TestComponent(
            name="alert", content='<div class="alert">{{ slot }}</div>'
        ).create(templates_dir)
        alert_css = TestAsset(
            component=alert, content=".alert { color: red; }", asset_type=AssetType.CSS
        ).create()
        alert_js = TestAsset(
            component=alert, content="console.log('alert');", asset_type=AssetType.JS
        ).create()

        button = TestComponent(
            name="button", content="<button>{{ slot }}</button>"
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()
        button_js = TestAsset(
            component=button, content="console.log('button');", asset_type=AssetType.JS
        ).create()

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

        registry.discover_components()

        template = create_template(child_path)

        rendered = template.render({})

        assert (
            f'<link rel="stylesheet" href="/__bird__/assets/{alert.name}/{alert_css.file.name}">'
            in rendered
        )
        assert (
            f'<link rel="stylesheet" href="/__bird__/assets/{button.name}/{button_css.file.name}">'
            in rendered
        )
        assert (
            f'<script src="/__bird__/assets/{alert.name}/{alert_js.file.name}"></script>'
            in rendered
        )
        assert (
            f'<script src="/__bird__/assets/{button.name}/{button_js.file.name}"></script>'
            in rendered
        )

    def test_with_no_assets(self, create_template, templates_dir):
        TestComponent(
            name="alert", content='<div class="alert">{{ slot }}</div>'
        ).create(templates_dir)

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

    def test_component_render_order(self, create_template, templates_dir, registry):
        first = TestComponent(
            name="first", content="<div>First: {{ slot }}</div>"
        ).create(templates_dir)
        first_css = TestAsset(
            component=first, content=".first { color: red; }", asset_type=AssetType.CSS
        ).create()
        first_js = TestAsset(
            component=first, content="console.log('first');", asset_type=AssetType.JS
        ).create()

        second = TestComponent(
            name="second", content="<div>Second: {{ slot }}</div>"
        ).create(templates_dir)
        second_css = TestAsset(
            component=second,
            content=".second { color: red; }",
            asset_type=AssetType.CSS,
        ).create()
        second_js = TestAsset(
            component=second, content="console.log('second');", asset_type=AssetType.JS
        ).create()

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

        registry.discover_components()

        template = create_template(template_path)

        rendered = template.render({})

        head_end = rendered.find("</head>")
        assert (
            f'<link rel="stylesheet" href="/__bird__/assets/{first.name}/{first_css.file.name}">'
            in rendered[:head_end]
        )
        assert (
            f'<link rel="stylesheet" href="/__bird__/assets/{second.name}/{second_css.file.name}">'
            in rendered[:head_end]
        )

        body_start = rendered.find("<body")
        assert (
            f'<script src="/__bird__/assets/{first.name}/{first_js.file.name}"></script>'
            in rendered[body_start:]
        )
        assert (
            f'<script src="/__bird__/assets/{second.name}/{second_js.file.name}"></script>'
            in rendered[body_start:]
        )

    def test_asset_duplication(self, create_template, templates_dir, registry):
        alert = TestComponent(
            name="alert", content='<div class="alert">{{ slot }}</div>'
        ).create(templates_dir)
        alert_css = TestAsset(
            component=alert, content=".alert { color: red; }", asset_type=AssetType.CSS
        ).create()
        alert_js = TestAsset(
            component=alert, content="console.log('alert');", asset_type=AssetType.JS
        ).create()

        base_path = templates_dir / "base.html"
        base_path.write_text("""
            <html>
            <head>
                <title>Test</title>
                {% bird:css %}
            </head>
            <body>
                {% bird alert %}Base Alert{% endbird %}
                {% bird alert %}Base Alert{% endbird %}
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
                {% bird alert %}Base Alert{% endbird %}
                {% bird alert %}Base Alert{% endbird %}
                {% bird alert %}Base Alert{% endbird %}
            {% endblock %}
        """)

        registry.discover_components()

        template = get_template(child_path.name)

        rendered = template.render({})
        print(f"{rendered=}")

        assert (
            rendered.count(
                f'<link rel="stylesheet" href="/__bird__/assets/{alert.name}/{alert_css.file.name}">'
            )
            == 1
        )
        assert (
            rendered.count(
                f'<script src="/__bird__/assets/{alert.name}/{alert_js.file.name}"></script>'
            )
            == 1
        )

    def test_unused_component_asset_not_rendered(
        self, create_template, templates_dir, registry
    ):
        alert = TestComponent(
            name="alert", content='<div class="alert">{{ slot }}</div>'
        ).create(templates_dir)
        alert_css = TestAsset(
            component=alert, content=".alert { color: red; }", asset_type=AssetType.CSS
        ).create()
        alert_js = TestAsset(
            component=alert, content="console.log('alert');", asset_type=AssetType.JS
        ).create()

        button = TestComponent(
            name="button", content="<button>{{ slot }}</button>"
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()
        button_js = TestAsset(
            component=button, content="console.log('button');", asset_type=AssetType.JS
        ).create()

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
                {% bird alert %}Base Alert{% endbird %}
            {% endblock %}
        """)

        registry.discover_components()

        template = create_template(child_path)

        rendered = template.render({})

        assert (
            f'<link rel="stylesheet" href="/__bird__/assets/{alert.name}/{alert_css.file.name}">'
            in rendered
        )
        assert (
            f'<script src="/__bird__/assets/{alert.name}/{alert_js.file.name}"></script>'
            in rendered
        )
        assert (
            f'<link rel="stylesheet" href="/__bird__/assets/{button.name}/{button_css.file.name}">'
            not in rendered
        )
        assert (
            f'<script src="/__bird__/assets/{button.name}/{button_js.file.name}"></script>'
            not in rendered
        )


class TestNode:
    def test_no_template(self):
        node = AssetNode(AssetType.CSS)
        context = Context({})
        assert node.render(context) == ""
