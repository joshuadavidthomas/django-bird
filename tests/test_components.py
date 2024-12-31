from __future__ import annotations

from pathlib import Path

import pytest
from django.template.backends.django import Template
from django.template.exceptions import TemplateDoesNotExist
from django.test import override_settings

from django_bird.components import Component
from django_bird.components import ComponentRegistry
from django_bird.staticfiles import Asset
from django_bird.staticfiles import AssetType


class TestComponent:
    def test_from_name_basic(self, create_bird_template):
        create_bird_template("button", "<button>Click me</button>")

        comp = Component.from_name("button")

        assert comp.name == "button"
        assert comp.assets == frozenset()
        assert isinstance(comp.template, Template)
        assert comp.render({}) == "<button>Click me</button>"

    def test_from_name_with_assets(self, create_template, create_bird_template):
        template_file = create_bird_template("button", "<button>Click me</button>")
        create_template(template_file)

        css_file = template_file.with_suffix(".css")
        js_file = template_file.with_suffix(".js")
        css_file.write_text("button { color: red; }")
        js_file.write_text("console.log('loaded');")

        comp = Component.from_name("button")

        assert len(comp.assets) == 2
        assert Asset(css_file, AssetType.CSS) in comp.assets
        assert Asset(js_file, AssetType.JS) in comp.assets

    @pytest.mark.parametrize(
        "suffix,content,expected_type",
        [
            (".css", "button { color: red; }", AssetType.CSS),
            (".js", "console.log('loaded');", AssetType.JS),
        ],
    )
    def test_from_name_with_partial_assets(
        self, suffix, content, expected_type, create_template, create_bird_template
    ):
        template_file = create_bird_template("button", "<button>Click me</button>")
        create_template(template_file)

        file = template_file.with_suffix(suffix)
        file.write_text(content)

        comp = Component.from_name("button")

        assert len(comp.assets) == 1
        assert Asset(file, expected_type) in comp.assets

    def test_from_name_no_assets(self, create_template, create_bird_template):
        template_file = create_bird_template("button", "<button>Click me</button>")
        create_template(template_file)

        comp = Component.from_name("button")

        assert len(comp.assets) == 0

    def test_from_name_custom_component_dir(
        self, create_template, create_bird_template
    ):
        template_file = create_bird_template(
            name="button", content="<button>", sub_dir="components"
        )

        css_file = template_file.with_suffix(".css")
        css_file.write_text("button { color: red; }")

        create_template(template_file)

        comp = Component.from_name("components/button")

        assert len(comp.assets) == 1
        assert Asset(css_file, AssetType.CSS) in comp.assets


class TestComponentRegistry:
    @pytest.fixture
    def registry(self):
        return ComponentRegistry(maxsize=2)

    def test_get_component_caches(self, registry, create_bird_template):
        create_bird_template(name="button", content="<button>Click me</button>")

        component1 = registry.get_component("button")
        component2 = registry.get_component("button")

        assert component1 is component2

    def test_lru_cache_behavior(self, registry, create_bird_template):
        create_bird_template(name="button1", content="1")
        create_bird_template(name="button2", content="2")
        create_bird_template(name="button3", content="3")

        button1 = registry.get_component("button1")
        button2 = registry.get_component("button2")
        button3 = registry.get_component("button3")

        new_button1 = registry.get_component("button1")
        assert new_button1 is not button1

        cached_button2 = registry.get_component("button2")
        assert cached_button2.name == button2.name
        assert cached_button2.render({}) == button2.render({})

        cached_button3 = registry.get_component("button3")
        assert cached_button3.name == button3.name
        assert cached_button3.render({}) == button3.render({})

    def test_component_not_found(self, registry):
        with pytest.raises(TemplateDoesNotExist):
            registry.get_component("nonexistent")

    def test_cache_with_debug(self, registry, create_bird_template):
        create_bird_template(name="button", content="<button>Click me</button>")

        assert len(registry._components) == 0

        with override_settings(DEBUG=True):
            registry.get_component("button")

        assert len(registry._components) == 0

        registry.get_component("button")

        assert len(registry._components) == 1

    def test_get_assets_by_type(
        self, registry, create_bird_template, create_bird_asset
    ):
        template_file = create_bird_template("test", "<div>Test</div>")
        css_asset = create_bird_asset(template_file, ".test { color: red; }", "css")
        js_asset = create_bird_asset(template_file, "console.log('test');", "js")

        registry.get_component(
            "test"
        )  # This now registers the component and its assets

        css_assets = registry.get_assets(AssetType.CSS)
        js_assets = registry.get_assets(AssetType.JS)

        assert len(css_assets) == 1
        assert len(js_assets) == 1
        assert Asset(Path(css_asset), AssetType.CSS) in css_assets
        assert Asset(Path(js_asset), AssetType.JS) in js_assets

    def test_multiple_components_same_asset_names(
        self, registry, create_bird_template, create_bird_asset
    ):
        template1 = create_bird_template("comp1", "<div>One</div>", sub_dir="first")
        template2 = create_bird_template("comp2", "<div>Two</div>", sub_dir="second")

        css1 = create_bird_asset(template1, ".one { color: red; }", "css")
        css2 = create_bird_asset(template2, ".two { color: blue; }", "css")

        registry.get_component("first/comp1")
        registry.get_component("second/comp2")

        css_assets = registry.get_assets(AssetType.CSS)
        assert len(css_assets) == 2

        asset_paths = {str(asset.path) for asset in css_assets}
        assert str(css1) in asset_paths
        assert str(css2) in asset_paths

    def test_template_inheritance_assets(
        self,
        registry,
        create_bird_template,
        create_bird_asset,
        create_template,
        templates_dir,
    ):
        parent = create_bird_template("parent", "<div>Parent</div>")
        child = create_bird_template("child", "<div>Child</div>")

        parent_css = create_bird_asset(parent, ".parent { color: red; }", "css")
        child_css = create_bird_asset(child, ".child { color: blue; }", "css")

        base_path = templates_dir / "base.html"
        base_path.write_text("""
            {% bird parent %}Parent Content{% endbird %}
            {% block content %}{% endblock %}
        """)

        child_path = templates_dir / "child.html"
        child_path.write_text("""
            {% extends 'base.html' %}
            {% block content %}
                {% bird child %}Child Content{% endbird %}
            {% endblock %}
        """)

        # Pre-load the components so they're in the registry
        registry.get_component("parent")
        registry.get_component("child")

        template = create_template(child_path)
        template.render({})

        css_assets = registry.get_assets(AssetType.CSS)
        asset_paths = {str(asset.path) for asset in css_assets}

        assert str(parent_css) in asset_paths, "Parent CSS not found in assets"
        assert str(child_css) in asset_paths, "Child CSS not found in assets"

    def test_empty_registry(self, registry):
        assert len(registry._components) == 0
        assert len(registry.get_assets(AssetType.CSS)) == 0
        assert len(registry.get_assets(AssetType.JS)) == 0
