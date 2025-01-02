from __future__ import annotations

import pytest
from django.template.backends.django import Template
from django.template.exceptions import TemplateDoesNotExist
from django.test import override_settings

from django_bird.components import Component
from django_bird.components import ComponentRegistry
from django_bird.staticfiles import Asset
from django_bird.staticfiles import AssetType
from tests.conftest import TestAsset
from tests.conftest import TestComponent


class TestComponentClass:
    def test_from_name_basic(self, templates_dir):
        TestComponent(name="button", content="<button>Click me</button>").create(
            templates_dir
        )

        comp = Component.from_name("button")

        assert comp.name == "button"
        assert isinstance(comp.template, Template)
        assert comp.render({}) == "<button>Click me</button>"

    def test_from_name_with_assets(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()
        button_js = TestAsset(
            component=button, content="console.log('button');", asset_type=AssetType.JS
        ).create()

        comp = Component.from_name("button")

        assert comp.name == "button"
        assert len(comp.assets) == 2
        assert Asset(button_css.file, AssetType.CSS) in comp.assets
        assert Asset(button_js.file, AssetType.JS) in comp.assets

    def test_from_name_with_partial_assets_css(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        button_css = TestAsset(
            button, ".button { color: blue; }", asset_type=AssetType.CSS
        ).create()

        comp = Component.from_name("button")

        assert comp.name == "button"
        assert len(comp.assets) == 1
        assert Asset(button_css.file, button_css.asset_type) in comp.assets

    def test_from_name_with_partial_assets_js(self, templates_dir):
        button = TestComponent(name="button", content="<button>Click me</button>")
        button.create(templates_dir)

        button_js = TestAsset(
            button, "console.log('button');", asset_type=AssetType.JS
        ).create()

        comp = Component.from_name("button")

        assert comp.name == "button"
        assert len(comp.assets) == 1
        assert Asset(button_js.file, button_js.asset_type) in comp.assets

    def test_from_name_no_assets(self, templates_dir):
        button = TestComponent(name="button", content="<button>Click me</button>")
        button.create(templates_dir)

        comp = Component.from_name("button")

        assert len(comp.assets) == 0

    def test_from_name_custom_component_dir(self, templates_dir, override_app_settings):
        TestComponent(
            name="button", content="<button>Click me</button>", parent_dir="components"
        ).create(templates_dir)

        with override_app_settings(COMPONENT_DIRS=["components"]):
            comp = Component.from_name("button")

        assert comp.name == "button"
        assert isinstance(comp.template, Template)
        assert comp.render({}) == "<button>Click me</button>"


class TestComponentRegistry:
    @pytest.fixture
    def registry(self):
        return ComponentRegistry(maxsize=2)

    def test_initialize_loads_components(self, registry, templates_dir):
        TestComponent(name="button", content="<button>Click me</button>").create(
            templates_dir
        )
        TestComponent(name="alert", content="<div>Alert</div>").create(templates_dir)

        registry.discover_components()

        assert "button" in registry._components
        assert "alert" in registry._components

    def test_initialize_loads_assets(self, registry, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()
        TestAsset(
            component=button, content="console.log('button');", asset_type=AssetType.JS
        ).create()

        registry.discover_components()

        component = registry._components["button"]
        assert len(component.assets) == 2

    def test_initialize_with_custom_dirs(
        self, registry, templates_dir, override_app_settings
    ):
        TestComponent(
            name="button", content="<button>Click me</button>", parent_dir="components"
        ).create(templates_dir)

        with override_app_settings(COMPONENT_DIRS=["components"]):
            registry.discover_components()

        assert "button" in registry._components

    def test_initialize_handles_missing_dirs(self, registry, override_app_settings):
        with override_app_settings(COMPONENT_DIRS=["nonexistent"]):
            registry.discover_components()

    def test_initialize_handles_invalid_components(self, registry, tmp_path):
        component_dir = tmp_path / "bird" / "invalid"
        component_dir.mkdir(parents=True)

        registry.discover_components()

    def test_get_component_caches(self, registry, templates_dir):
        TestComponent(name="button", content="<button>Click me</button>").create(
            templates_dir
        )

        component1 = registry.get_component("button")
        component2 = registry.get_component("button")

        assert component1 is component2

    def test_lru_cache_behavior(self, registry, templates_dir):
        TestComponent(name="button1", content="<button>1</button>").create(
            templates_dir
        )
        TestComponent(name="button2", content="<button>2</button>").create(
            templates_dir
        )
        TestComponent(name="button3", content="<button>3</button>").create(
            templates_dir
        )

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

    def test_cache_with_debug(self, registry, templates_dir):
        TestComponent(name="button", content="<button>Click me</button>").create(
            templates_dir
        )

        assert len(registry._components) == 0

        with override_settings(DEBUG=True):
            registry.get_component("button")

        assert len(registry._components) == 0

        registry.get_component("button")

        assert len(registry._components) == 1

    def test_get_assets_by_type(self, registry, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        button_css = TestAsset(
            component=button,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()
        button_js = TestAsset(
            component=button, content="console.log('button');", asset_type=AssetType.JS
        ).create()

        registry.get_component("button")

        css_assets = registry.get_assets(AssetType.CSS)
        js_assets = registry.get_assets(AssetType.JS)

        assert len(css_assets) == 1
        assert len(js_assets) == 1
        assert Asset(button_css.file, AssetType.CSS) in css_assets
        assert Asset(button_js.file, AssetType.JS) in js_assets

    def test_multiple_components_same_asset_names(self, registry, templates_dir):
        button1 = TestComponent(
            name="button1", content="<button>Click me</button>"
        ).create(templates_dir)
        button2 = TestComponent(
            name="button2", content="<button>Click me</button>"
        ).create(templates_dir)

        button1_css = TestAsset(
            component=button1,
            content=".button { color: red; }",
            asset_type=AssetType.CSS,
        ).create()
        button2_css = TestAsset(
            component=button2,
            content=".button { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        registry.get_component("button1")
        registry.get_component("button2")

        css_assets = registry.get_assets(AssetType.CSS)
        assert len(css_assets) == 2

        asset_paths = {str(asset.path) for asset in css_assets}
        assert str(button1_css.file) in asset_paths
        assert str(button2_css.file) in asset_paths

    def test_empty_registry(self, registry):
        assert len(registry._components) == 0
        assert len(registry.get_assets(AssetType.CSS)) == 0
        assert len(registry.get_assets(AssetType.JS)) == 0
