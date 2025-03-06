from __future__ import annotations

import shutil

import pytest
from django.template.base import Parser
from django.template.base import Token
from django.template.base import TokenType
from django.template.context import Context
from django.template.exceptions import TemplateSyntaxError
from django.template.loader import get_template
from django.test import override_settings

from django_bird.manifest import generate_asset_manifest
from django_bird.manifest import save_asset_manifest
from django_bird.staticfiles import CSS
from django_bird.staticfiles import JS
from django_bird.templatetags.tags.asset import AssetNode
from django_bird.templatetags.tags.asset import AssetTag
from django_bird.templatetags.tags.asset import do_asset
from tests.utils import TestAsset
from tests.utils import TestComponent


class TestTemplateTag:
    @pytest.mark.parametrize(
        "tag,expected",
        [
            (AssetTag.CSS.value, AssetTag.CSS),
            (AssetTag.JS.value, AssetTag.JS),
        ],
    )
    def test_asset_type(self, tag, expected):
        token = Token(TokenType.BLOCK, tag)
        parser = Parser([])
        node = do_asset(parser, token)
        assert node.asset_tag == expected

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
            component=alert, content=".alert { color: red; }", asset_type=CSS
        ).create()
        alert_js = TestAsset(
            component=alert, content="console.log('alert');", asset_type=JS
        ).create()

        button = TestComponent(
            name="button", content="<button>{{ slot }}</button>"
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=CSS,
        ).create()
        button_js = TestAsset(
            component=button, content="console.log('button');", asset_type=JS
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

        template = create_template(child_path)

        rendered = template.render({})

        assert (
            f'<link rel="stylesheet" href="/static/django_bird/bird/{alert_css.file.name}">'
            in rendered
        )
        assert (
            f'<link rel="stylesheet" href="/static/django_bird/bird/{button_css.file.name}">'
            in rendered
        )
        assert (
            f'<script src="/static/django_bird/bird/{alert_js.file.name}"></script>'
            in rendered
        )
        assert (
            f'<script src="/static/django_bird/bird/{button_js.file.name}"></script>'
            in rendered
        )

    def test_template_inheritence_no_bird_usage(
        self, create_template, templates_dir, registry
    ):
        alert = TestComponent(
            name="alert", content='<div class="alert">{{ slot }}</div>'
        ).create(templates_dir)
        alert_css = TestAsset(
            component=alert, content=".alert { color: red; }", asset_type=CSS
        ).create()
        alert_js = TestAsset(
            component=alert, content="console.log('alert');", asset_type=JS
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
                No bird component here!
            {% endblock %}
        """)

        template = create_template(child_path)

        rendered = template.render({})

        assert (
            f'<link rel="stylesheet" href="/static/django_bird/bird/{alert_css.file.name}">'
            in rendered
        )
        assert (
            f'<script src="/static/django_bird/bird/{alert_js.file.name}"></script>'
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
            component=first, content=".first { color: red; }", asset_type=CSS
        ).create()
        first_js = TestAsset(
            component=first, content="console.log('first');", asset_type=JS
        ).create()

        second = TestComponent(
            name="second", content="<div>Second: {{ slot }}</div>"
        ).create(templates_dir)
        second_css = TestAsset(
            component=second,
            content=".second { color: red; }",
            asset_type=CSS,
        ).create()
        second_js = TestAsset(
            component=second, content="console.log('second');", asset_type=JS
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

        template = create_template(template_path)

        rendered = template.render({})

        head_end = rendered.find("</head>")
        assert (
            f'<link rel="stylesheet" href="/static/django_bird/bird/{first_css.file.name}">'
            in rendered[:head_end]
        )
        assert (
            f'<link rel="stylesheet" href="/static/django_bird/bird/{second_css.file.name}">'
            in rendered[:head_end]
        )

        body_start = rendered.find("<body")
        assert (
            f'<script src="/static/django_bird/bird/{first_js.file.name}"></script>'
            in rendered[body_start:]
        )
        assert (
            f'<script src="/static/django_bird/bird/{second_js.file.name}"></script>'
            in rendered[body_start:]
        )

    def test_asset_duplication(self, create_template, templates_dir, registry):
        alert = TestComponent(
            name="alert", content='<div class="alert">{{ slot }}</div>'
        ).create(templates_dir)
        alert_css = TestAsset(
            component=alert, content=".alert { color: red; }", asset_type=CSS
        ).create()
        alert_js = TestAsset(
            component=alert, content="console.log('alert');", asset_type=JS
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

        template = get_template(child_path.name)

        rendered = template.render({})

        assert (
            rendered.count(
                f'<link rel="stylesheet" href="/static/django_bird/bird/{alert_css.file.name}">'
            )
            == 1
        )
        assert (
            rendered.count(
                f'<script src="/static/django_bird/bird/{alert_js.file.name}"></script>'
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
            component=alert, content=".alert { color: red; }", asset_type=CSS
        ).create()
        alert_js = TestAsset(
            component=alert, content="console.log('alert');", asset_type=JS
        ).create()

        button = TestComponent(
            name="button", content="<button>{{ slot }}</button>"
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=CSS,
        ).create()
        button_js = TestAsset(
            component=button, content="console.log('button');", asset_type=JS
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

        template = create_template(child_path)

        rendered = template.render({})

        assert (
            f'<link rel="stylesheet" href="/static/django_bird/bird/{alert_css.file.name}">'
            in rendered
        )
        assert (
            f'<script src="/static/django_bird/bird/{alert_js.file.name}"></script>'
            in rendered
        )
        assert (
            f'<link rel="stylesheet" href="/static/django_bird/bird/{button_css.file.name}">'
            not in rendered
        )
        assert (
            f'<script src="/static/django_bird/bird/{button_js.file.name}"></script>'
            not in rendered
        )


class TestNode:
    def test_no_template(self):
        node = AssetNode(CSS)
        context = Context({})
        assert node.render(context) == ""


class TestManifest:
    @pytest.fixture
    def static_root(self, tmp_path):
        static_dir = tmp_path / "static"
        static_dir.mkdir()

        with override_settings(STATIC_ROOT=str(static_dir)):
            yield static_dir

        shutil.rmtree(static_dir)

    def test_asset_tag_with_manifest_in_production(
        self, create_template, templates_dir, static_root, registry
    ):
        button = TestComponent(
            name="button", content="<button>{{ slot }}</button>"
        ).create(templates_dir)

        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=CSS,
        ).create()

        template_path = templates_dir / "manifest_test.html"
        template_path.write_text("""
        <html>
        <head>
            <title>Test</title>
            {% bird:css %}
        </head>
        <body>
            {% bird button %}Test Button{% endbird %}
        </body>
        </html>
        """)

        manifest_data = generate_asset_manifest()

        manifest_path = static_root / "django_bird"
        manifest_path.mkdir(parents=True)
        save_asset_manifest(manifest_data, manifest_path / "manifest.json")

        with override_settings(DEBUG=False):
            template = create_template(template_path)
            rendered = template.render({})

            assert (
                f'<link rel="stylesheet" href="/static/django_bird/bird/{button_css.file.name}">'
                in rendered
            )

    def test_asset_tag_in_debug_mode(
        self, create_template, templates_dir, static_root, registry
    ):
        button = TestComponent(
            name="button", content="<button>{{ slot }}</button>"
        ).create(templates_dir)

        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=CSS,
        ).create()

        template_path = templates_dir / "debug_test.html"
        template_path.write_text("""
        <html>
        <head>
            <title>Test</title>
            {% bird:css %}
        </head>
        <body>
            {% bird button %}Test Button{% endbird %}
        </body>
        </html>
        """)

        manifest_data = {"not/a/real/template.html": ["not-button"]}

        manifest_path = static_root / "django_bird"
        manifest_path.mkdir(parents=True)
        save_asset_manifest(manifest_data, manifest_path / "manifest.json")

        with override_settings(DEBUG=True):
            template = create_template(template_path)
            rendered = template.render({})

            assert (
                f'<link rel="stylesheet" href="/static/bird/{button_css.file.name}">'
                in rendered
            )

    def test_asset_tag_fallback_when_template_not_in_manifest(
        self, create_template, templates_dir, static_root, registry
    ):
        button = TestComponent(
            name="button", content="<button>{{ slot }}</button>"
        ).create(templates_dir)

        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=CSS,
        ).create()

        template_path = templates_dir / "not_in_manifest.html"
        template_path.write_text("""
        <html>
        <head>
            <title>Test</title>
            {% bird:css %}
        </head>
        <body>
            {% bird button %}Test Button{% endbird %}
        </body>
        </html>
        """)

        # Create a different template to put in the manifest
        other_path = templates_dir / "other_template.html"
        other_path.write_text("""
        <html><body>Other template</body></html>
        """)

        manifest_data = {str(other_path): ["button"]}

        manifest_path = static_root / "django_bird"
        manifest_path.mkdir(parents=True)
        save_asset_manifest(manifest_data, manifest_path / "manifest.json")

        with override_settings(DEBUG=False):
            template = create_template(template_path)
            rendered = template.render({})

            assert (
                f'<link rel="stylesheet" href="/static/django_bird/bird/{button_css.file.name}">'
                in rendered
            )

    def test_asset_tag_renders_nothing_when_no_component_found(
        self, create_template, templates_dir
    ):
        template_path = templates_dir / "no_components.html"
        template_path.write_text("""
        <html>
        <head>
            <title>Test</title>
            {% bird:css %}
        </head>
        <body>
            No bird components here
            {% bird:js %}
        </body>
        </html>
        """)

        template = create_template(template_path)
        rendered = template.render({})

        assert '<link rel="stylesheet"' not in rendered
        assert "<script src=" not in rendered
