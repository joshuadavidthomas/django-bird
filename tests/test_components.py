from __future__ import annotations

import pytest
from django.template.backends.django import Template
from django.test import override_settings
from django.template.exceptions import TemplateDoesNotExist

from django_bird.components import Component
from django_bird.components import Registry
from django_bird.staticfiles import Asset
from django_bird.staticfiles import AssetType


class TestComponent:
    def test_from_name_basic(self, create_bird_template):
        create_bird_template("button", "<button>Click me</button>")

        comp = Component.from_name("button")

        assert comp.name == "button"
        assert comp.assets == set()
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
        "asset_suffix,asset_content,expected_asset_type",
        [
            (".css", "button { color: red; }", AssetType.CSS),
            (".js", "console.log('loaded');", AssetType.JS),
        ],
    )
    def test_from_name_with_partial_assets(
        self,
        asset_suffix,
        asset_content,
        expected_asset_type,
        create_template,
        create_bird_template,
    ):
        template_file = create_bird_template("button", "<button>Click me</button>")
        create_template(template_file)

        file = template_file.with_suffix(asset_suffix)
        file.write_text(asset_content)

        comp = Component.from_name("button")

        assert len(comp.assets) == 1
        assert Asset(file, expected_asset_type) in comp.assets


class TestRegistry:
    @pytest.fixture
    def registry(self):
        return Registry(maxsize=2)

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

        assert len(registry._cache) == 0

        with override_settings(DEBUG=True):
            registry.get_component("button")

        assert len(registry._cache) == 0

        registry.get_component("button")

        assert len(registry._cache) == 1
