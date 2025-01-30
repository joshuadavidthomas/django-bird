from __future__ import annotations

import queue
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest
from django.template import Template
from django.template.backends.django import Template as DjangoTemplate
from django.template.context import Context
from django.template.exceptions import TemplateDoesNotExist
from django.test import override_settings

from django_bird.components import Component
from django_bird.components import ComponentRegistry
from django_bird.components import components
from django_bird.staticfiles import Asset
from django_bird.staticfiles import AssetType

from .utils import TestAsset
from .utils import TestComponent


class TestComponentClass:
    def test_from_abs_path_basic(self, templates_dir):
        test_component = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        component = Component.from_abs_path(
            test_component.file, test_component.file.parent
        )

        assert component is not None

    def test_from_name_basic(self, templates_dir):
        TestComponent(name="button", content="<button>Click me</button>").create(
            templates_dir
        )

        comp = Component.from_name("button")

        assert comp.name == "button"
        assert isinstance(comp.template, DjangoTemplate)

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
        assert isinstance(comp.template, DjangoTemplate)

    def test_id_is_consistent(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        comp1 = Component.from_name(button.name)
        comp2 = Component.from_name(button.name)

        assert comp1.id == comp2.id

    def test_id_content_changes(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        comp1 = Component.from_name(button.name)

        button.file.write_text("<button>Don't click me</button>")
        comp2 = Component.from_name(button.name)

        assert comp1.id != comp2.id

    def test_id_whitespace_changes(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        comp1 = Component.from_name(button.name)

        button.file.write_text("<button>\n  Click me\n</button>")
        comp2 = Component.from_name(button.name)

        assert comp1.id == comp2.id

    def test_id_name_changes(self, templates_dir):
        button1 = TestComponent(
            name="button1", content="<button>Click me</button>"
        ).create(templates_dir)
        button2 = TestComponent(
            name="button2", content="<button>Click me</button>"
        ).create(templates_dir)

        comp1 = Component.from_name(button1.name)
        comp2 = Component.from_name(button2.name)

        assert comp1.id != comp2.id

    def test_id_formatting(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        comp = Component.from_name(button.name)

        assert len(comp.id) == 7
        assert all(c in "0123456789abcdef" for c in comp.id)

    def test_data_attribute_name_basic(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        comp = Component.from_name(button.name)

        assert comp.data_attribute_name == "button"

    def test_data_attribute_name_nested(self, templates_dir):
        button = TestComponent(
            name="button",
            content="<button>Nested</button>",
            sub_dir="nested",
        ).create(templates_dir)

        comp = Component.from_name(f"{button.sub_dir}.{button.name}")

        assert comp.data_attribute_name == "nested-button"


class TestBoundComponent:
    @pytest.mark.parametrize(
        "attr_app_setting,expected",
        [
            ({"ENABLE_BIRD_ATTRS": True}, True),
            ({"ENABLE_BIRD_ATTRS": False}, False),
        ],
    )
    def test_id_sequence(
        self,
        attr_app_setting,
        expected,
        override_app_settings,
        templates_dir,
        normalize_whitespace,
    ):
        button = TestComponent(
            name="button", content="<button {{ attrs }}>{{ slot }}</button>"
        ).create(templates_dir)
        comp = Component.from_name(button.name)

        template = Template("""
            {% bird button class="btn" %}
                Click me once
            {% endbird %}
            {% bird button class="btn" %}
                Click me twice
            {% endbird %}
            {% bird button class="btn" %}
                Click me three times a lady
            {% endbird %}
        """)

        with override_app_settings(**attr_app_setting):
            rendered = template.render(Context({}))

        assert (
            normalize_whitespace(rendered)
            == normalize_whitespace(f"""
                <button class="btn" data-bird-button data-bird-id="{comp.id}-1">
                    Click me once
                </button>
                <button class="btn" data-bird-button data-bird-id="{comp.id}-2">
                    Click me twice
                </button>
                <button class="btn" data-bird-button data-bird-id="{comp.id}-3">
                    Click me three times a lady
                </button>
            """)
        ) is expected


class TestComponentRegistryProject:
    def test_discover_components(self, templates_dir):
        TestComponent(name="button", content="<button>Click me</button>").create(
            templates_dir
        )
        TestComponent(name="alert", content="<div>Alert</div>").create(templates_dir)

        components.discover_components()

        assert "button" in components._components
        assert "alert" in components._components

    def test_custom_dir(self, templates_dir, override_app_settings):
        TestComponent(
            name="button", content="<button>Click me</button>", parent_dir="components"
        ).create(templates_dir)

        with override_app_settings(COMPONENT_DIRS=["components"]):
            components.discover_components()

        assert "button" in components._components

    def test_missing_dir(self, override_app_settings):
        with override_app_settings(COMPONENT_DIRS=["nonexistent"]):
            components.discover_components()

        assert len(components._components) == 0

    def test_non_html_files(self, templates_dir):
        (templates_dir / "README.md").write_text("# Components")
        (templates_dir / "ignored.txt").write_text("Not a component")

        components.discover_components()

        assert len(components._components) == 0

    def test_empty_dirs(self, templates_dir):
        bird_dir = templates_dir / "bird"
        bird_dir.mkdir(parents=True)
        (bird_dir / "empty").mkdir()

        components.discover_components()

        assert len(components._components) == 0

    def test_nested_components(self, templates_dir):
        TestComponent(
            name="button",
            content="<button>Nested</button>",
            sub_dir="nested",
        ).create(templates_dir)

        components.discover_components()

        assert "nested.button" in components._components

    def test_component_name_collision(self, templates_dir, override_app_settings):
        TestComponent(
            name="button", content="<button>First</button>", parent_dir="first"
        ).create(templates_dir)

        TestComponent(
            name="button", content="<button>Second</button>", parent_dir="second"
        ).create(templates_dir)

        with override_app_settings(COMPONENT_DIRS=["first", "second"]):
            components.discover_components()
            component = components.get_component("button")
            assert "First" in component.template.template.source
            assert "Second" not in component.template.template.source

        components.reset()

        with override_app_settings(COMPONENT_DIRS=["second", "first"]):
            components.discover_components()
            component = components.get_component("button")
            assert "Second" in component.template.template.source
            assert "First" not in component.template.template.source


class TestComponentRegistryApps:
    @classmethod
    def setup_class(cls):
        cls.tmp_dir = tempfile.mkdtemp()
        cls.tmp_path = Path(cls.tmp_dir)

        sys.path.insert(0, str(cls.tmp_path))

        cls.app1_dir = cls.tmp_path / "test_app1"
        cls.app2_dir = cls.tmp_path / "test_app2"

        for app_dir in [cls.app1_dir, cls.app2_dir]:
            templates_dir = app_dir / "templates"
            templates_dir.mkdir(parents=True)

            (app_dir / "__init__.py").touch()

            (app_dir / "apps.py").write_text(f"""
from django.apps import AppConfig

class {app_dir.name.capitalize()}Config(AppConfig):
    name = '{app_dir.name}'
    path = '{str(app_dir)}'
""")

    @classmethod
    def teardown_class(cls):
        sys.path.remove(str(cls.tmp_path))
        shutil.rmtree(cls.tmp_dir)

    def test_discover_components_from_app(self):
        app1_templates = self.app1_dir / "templates"

        TestComponent(name="app1_button", content="<button>App1</button>").create(
            app1_templates
        )

        with override_settings(INSTALLED_APPS=["test_app1"]):
            components.discover_components()

        assert "app1_button" in components._components

    def test_multiple_apps_components(self):
        TestComponent(name="app1_button", content="<button>App1</button>").create(
            self.app1_dir / "templates"
        )

        TestComponent(name="app2_button", content="<button>App2</button>").create(
            self.app2_dir / "templates"
        )

        with override_settings(INSTALLED_APPS=["test_app1", "test_app2"]):
            components.discover_components()

        assert "app1_button" in components._components
        assert "app2_button" in components._components

    def test_app_component_override_project(self, templates_dir):
        TestComponent(name="button", content="<button>Project</button>").create(
            templates_dir
        )
        TestComponent(name="button", content="<button>App</button>").create(
            self.app1_dir / "templates"
        )

        with override_settings(INSTALLED_APPS=["test_app1"]):
            components.discover_components()
            component = components.get_component("button")
            assert "Project" in component.template.template.source
            assert "App" not in component.template.template.source

    def test_app_order_precedence(self):
        TestComponent(name="button", content="<button>App1</button>").create(
            self.app1_dir / "templates"
        )
        TestComponent(name="button", content="<button>App2</button>").create(
            self.app2_dir / "templates"
        )

        with override_settings(INSTALLED_APPS=["test_app1", "test_app2"]):
            components.discover_components()
            component = components.get_component("button")
            assert "App1" in component.template.template.source
            assert "App2" not in component.template.template.source

        components.reset()

        with override_settings(INSTALLED_APPS=["test_app2", "test_app1"]):
            components.discover_components()
            component = components.get_component("button")
            assert "App2" in component.template.template.source
            assert "App1" not in component.template.template.source


class TestComponentRegistryAssets:
    def test_discover_component_with_css(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        button_css = TestAsset(
            component=button,
            content=".button { color: red; }",
            asset_type=AssetType.CSS,
        ).create()

        components.discover_components()

        assert "button" in components._components

        component = components._components["button"]

        assert len(component.assets) == 1
        assert Asset(button_css.file, button_css.asset_type) in component.assets

    def test_discover_component_with_js(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        button_js = TestAsset(
            component=button,
            content="console.log('clicked');",
            asset_type=AssetType.JS,
        ).create()

        components.discover_components()

        assert "button" in components._components

        component = components._components["button"]

        assert len(component.assets) == 1
        assert Asset(button_js.file, button_js.asset_type) in component.assets

    def test_get_assets_by_type(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: red; }",
            asset_type=AssetType.CSS,
        ).create()
        button_js = TestAsset(
            component=button,
            content="console.log('loaded');",
            asset_type=AssetType.JS,
        ).create()

        components.discover_components()

        css_assets = components.get_assets(AssetType.CSS)
        js_assets = components.get_assets(AssetType.JS)

        assert len(css_assets) == 1
        assert len(js_assets) == 1
        assert Asset(button_css.file, button_css.asset_type) in css_assets
        assert Asset(button_js.file, button_js.asset_type) in js_assets

    def test_get_assets_all(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)
        button_css = TestAsset(
            component=button,
            content=".button { color: red; }",
            asset_type=AssetType.CSS,
        ).create()
        button_js = TestAsset(
            component=button,
            content="console.log('loaded');",
            asset_type=AssetType.JS,
        ).create()

        components.discover_components()

        assets = components.get_assets()

        assert len(assets) == 2
        assert Asset(button_css.file, button_css.asset_type) in assets
        assert Asset(button_js.file, button_js.asset_type) in assets

    def test_assets_from_multiple_components(self, templates_dir):
        button1 = TestComponent(name="button1", content="<button>One</button>").create(
            templates_dir
        )
        button2 = TestComponent(name="button2", content="<button>Two</button>").create(
            templates_dir
        )

        button1_css = TestAsset(
            component=button1,
            content=".button1 { color: red; }",
            asset_type=AssetType.CSS,
        ).create()
        button2_css = TestAsset(
            component=button2,
            content=".button2 { color: blue; }",
            asset_type=AssetType.CSS,
        ).create()

        components.discover_components()

        css_assets = components.get_assets(AssetType.CSS)

        assert len(css_assets) == 2
        assert Asset(button1_css.file, button1_css.asset_type) in css_assets
        assert Asset(button2_css.file, button2_css.asset_type) in css_assets

    def test_missing_asset_file(self, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        TestAsset(
            component=button,
            content="/* Missing */",
            asset_type=AssetType.CSS,
        )

        components.discover_components()

        assert "button" in components._components

        component = components._components["button"]

        assert len(component.assets) == 0


class TestComponentRegistryCaching:
    def test_debug_mode_caching(self, templates_dir):
        component = TestComponent(
            name="button", content="<button>Original</button>"
        ).create(templates_dir)

        with override_settings(DEBUG=True):
            first = components.get_component("button")

            assert "button" in components._components
            assert "Original" in first.template.template.source

            component.file.write_text("<button>Updated</button>")
            second = components.get_component("button")

            assert second is not first
            assert "Updated" in second.template.template.source

    def test_production_mode_caching(self, templates_dir):
        component = TestComponent(
            name="button", content="<button>Original</button>"
        ).create(templates_dir)

        with override_settings(DEBUG=False):
            first = components.get_component("button")

            component.file.write_text("<button>Updated</button>")
            second = components.get_component("button")

            assert second is first
            assert "Original" in second.template.template.source

    @pytest.mark.parametrize("debug", [True, False])
    def test_asset_tracking(self, debug, templates_dir):
        button = TestComponent(
            name="button", content="<button>Click me</button>"
        ).create(templates_dir)

        button_css = TestAsset(
            component=button,
            content=".button { color: red; }",
            asset_type=AssetType.CSS,
        ).create()

        with override_settings(DEBUG=debug):
            components.get_component("button")
            css_assets = components.get_assets(AssetType.CSS)

            assert len(css_assets) == 1
            assert Asset(button_css.file, button_css.asset_type) in css_assets

    def test_lru_cache_limit(self, templates_dir):
        small_registry = ComponentRegistry(maxsize=2)

        for i in range(3):
            TestComponent(
                name=f"button{i}", content=f"<button>Button {i}</button>"
            ).create(templates_dir)

        small_registry.get_component("button0")
        small_registry.get_component("button1")
        small_registry.get_component("button2")  # This should evict button0

        assert "button0" not in small_registry._components
        assert "button1" in small_registry._components
        assert "button2" in small_registry._components

    def test_cache_clear_with_reset(self, templates_dir):
        TestComponent(name="button", content="<button>Clear Me</button>").create(
            templates_dir
        )

        with override_settings(DEBUG=False):
            components.get_component("button")
            assert "button" in components._components

            components.reset()
            assert len(components._components) == 0

    def test_lru_cache_eviction_order(self, templates_dir):
        small_registry = ComponentRegistry(maxsize=2)

        for i in range(3):
            TestComponent(
                name=f"button{i}", content=f"<button>Button {i}</button>"
            ).create(templates_dir)

        small_registry.get_component("button0")
        small_registry.get_component("button1")

        # Access button0 again to make it more recently used than button1
        small_registry.get_component("button0")

        # Access button2, should evict button1 (least recently used)
        small_registry.get_component("button2")

        assert "button0" in small_registry._components
        assert "button1" not in small_registry._components
        assert "button2" in small_registry._components

    def test_concurrent_cache_access(self, templates_dir):
        TestComponent(name="shared_button", content="<button>Shared</button>").create(
            templates_dir
        )

        results = queue.Queue()

        def access_component():
            try:
                component = components.get_component("shared_button")
                results.put(("success", component.template.template.source))
            except Exception as e:
                results.put(("error", str(e)))

        # Create multiple threads to access the cache concurrently
        threads = [threading.Thread(target=access_component) for _ in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Check that all accesses were successful
        while not results.empty():
            status, result = results.get()
            assert status == "success"
            assert "Shared" in result

    def test_cache_memory_limit(self, templates_dir):
        large_registry = ComponentRegistry(maxsize=5)
        large_content = "x" * 1_000_000  # 1MB of content

        for i in range(6):
            TestComponent(
                name=f"large_button{i}", content=f"<button>{large_content}</button>"
            ).create(templates_dir)

            large_registry.get_component(f"large_button{i}")

        assert len(large_registry._components) <= 5


class TestComponentRegistryErrors:
    def test_invalid_template_syntax(self, templates_dir):
        invalid_template = templates_dir / "invalid.html"
        invalid_template.write_text("{% invalid syntax %}")

        components.discover_components()

        with pytest.raises(TemplateDoesNotExist):
            components.get_component("invalid")

    def test_missing_required_template(self):
        components.discover_components()

        with pytest.raises(TemplateDoesNotExist):
            components.get_component("nonexistent")

    def test_invalid_asset_reference(self, templates_dir):
        button = TestComponent(name="button", content="<button>Error</button>").create(
            templates_dir
        )

        TestAsset(
            component=button,
            content="/* Invalid */",
            asset_type="invalid_type",
        )

        components.discover_components()

        assert "button" in components._components

        component = components._components["button"]

        assert len(component.assets) == 0


class TestComponentRegistryPerformance:
    def test_large_directory_scan(self, templates_dir):
        for i in range(100):
            TestComponent(
                name=f"button{i}", content=f"<button>Button {i}</button>"
            ).create(templates_dir)

        start_time = time.time()

        components.discover_components()

        end_time = time.time()
        scan_duration = end_time - start_time

        assert len(components._components) == 100
        assert scan_duration < 1.0

    def test_deep_directory_structure(self, templates_dir):
        current_dir = templates_dir
        depth = 10

        for i in range(depth):
            current_dir = current_dir / f"level{i}"
            current_dir.mkdir()
            TestComponent(
                name=f"button{i}",
                content=f"<button>Nested level {i}</button>",
                sub_dir="/".join(f"level{j}" for j in range(i + 1)),
            ).create(templates_dir)

        start_time = time.time()

        components.discover_components()

        end_time = time.time()
        scan_duration = end_time - start_time

        assert len(components._components) == depth
        assert scan_duration < 1.0

    def test_repeated_access_performance(self, templates_dir):
        TestComponent(name="button", content="<button>Performance</button>").create(
            templates_dir
        )

        # uncached
        start_time = time.time()
        components.get_component("button")
        first_access = time.time() - start_time

        # should be cached
        start_time = time.time()
        components.get_component("button")
        cached_access = time.time() - start_time

        # Cached access should be significantly faster
        assert cached_access < first_access / 2
