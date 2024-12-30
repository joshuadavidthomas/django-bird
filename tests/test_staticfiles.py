from __future__ import annotations

from pathlib import Path

import pytest

from django_bird.components import components
from django_bird.staticfiles import Asset
from django_bird.staticfiles import AssetType
from django_bird.staticfiles import asset_registry
from django_bird.staticfiles import get_template_assets


class TestAsset:
    def test_hash(self):
        asset1 = Asset(Path("static.css"), AssetType.CSS)
        asset2 = Asset(Path("static.css"), AssetType.CSS)

        assert asset1 == asset2
        assert hash(asset1) == hash(asset2)

        assets = {asset1, asset2, Asset(Path("other.css"), AssetType.CSS)}

        assert len(assets) == 2

    def test_exists(self, tmp_path: Path):
        css_file = tmp_path / "test.css"
        css_file.touch()

        asset = Asset(css_file, AssetType.CSS)

        assert asset.exists() is True

    def test_exists_nonexistent(self):
        missing_asset = Asset(Path("missing.css"), AssetType.CSS)
        assert missing_asset.exists() is False

    @pytest.mark.parametrize(
        "path,expected",
        [
            (Path("static.css"), Asset(Path("static.css"), AssetType.CSS)),
            (Path("static.js"), Asset(Path("static.js"), AssetType.JS)),
            (
                Path("nested/path/style.css"),
                Asset(Path("nested/path/style.css"), AssetType.CSS),
            ),
            (
                Path("./relative/script.js"),
                Asset(Path("./relative/script.js"), AssetType.JS),
            ),
            (Path("UPPERCASE.CSS"), Asset(Path("UPPERCASE.CSS"), AssetType.CSS)),
            (Path("mixed.Js"), Asset(Path("mixed.Js"), AssetType.JS)),
        ],
    )
    def test_from_path(self, path, expected):
        assert Asset.from_path(path) == expected

    def test_from_path_invalid(self):
        with pytest.raises(ValueError):
            Asset.from_path(Path("static.html"))


class TestGetTemplateAssets:
    def test_with_assets(self, create_template, create_bird_template):
        template_file = create_bird_template(name="button", content="<button>")

        css_file = template_file.with_suffix(".css")
        js_file = template_file.with_suffix(".js")
        css_file.write_text("button { color: red; }")
        js_file.write_text("console.log('loaded');")

        template = create_template(template_file)
        assets = get_template_assets(template)

        assert len(assets) == 2
        assert Asset(css_file, AssetType.CSS) in assets
        assert Asset(js_file, AssetType.JS) in assets

    @pytest.mark.parametrize(
        "suffix,content,expected_type",
        [
            (".css", "button { color: red; }", AssetType.CSS),
            (".js", "console.log('loaded');", AssetType.JS),
        ],
    )
    def test_partial_assets(
        self, suffix, content, expected_type, create_template, create_bird_template
    ):
        template_file = create_bird_template(name="button", content="<button>")

        file = template_file.with_suffix(suffix)
        file.write_text(content)

        template = create_template(template_file)

        assets = get_template_assets(template)

        assert len(assets) == 1
        assert Asset(file, expected_type) in assets

    def test_no_assets(self, create_template, create_bird_template):
        template_file = create_bird_template(name="button", content="<button>")

        template = create_template(template_file)

        assets = get_template_assets(template)

        assert len(assets) == 0

    def test_custom_component_dir(self, create_template, create_bird_template):
        template_file = create_bird_template(
            name="button", content="<button>", sub_dir="components"
        )

        css_file = template_file.with_suffix(".css")
        css_file.write_text("button { color: red; }")

        template = create_template(template_file)

        assets = get_template_assets(template)

        assert len(assets) == 1
        assert Asset(css_file, AssetType.CSS) in assets


class TestComponentAssetRegistry:
    def test_asset_registry(
        self, create_bird_template, create_bird_asset, create_template, templates_dir
    ):
        alert = create_bird_template("alert", '<div class="alert">{{ slot }}</div>')
        create_bird_asset(alert, ".alert { color: red; }", "css")
        create_bird_asset(alert, "console.log('alert');", "js")

        badge = create_bird_template("badge", "<span>{{ slot }}</span>")
        create_bird_asset(badge, ".badge { color: blue; }", "css")
        create_bird_asset(badge, "console.log('badge');", "js")

        button = create_bird_template("button", "<button>{{ slot }}</button>")
        create_bird_asset(button, ".button { color: blue; }", "css")
        create_bird_asset(button, "console.log('button');", "js")

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

        include_path = templates_dir / "include.html"
        include_path.write_text("""
            {% bird badge %}Active{% endbird %}
        """)

        child_path = templates_dir / "child.html"
        child_path.write_text("""
            {% extends 'base.html' %}
            {% block content %}
                {% bird button %}Click me{% endbird %}
                {% include 'include.html' %}
            {% endblock %}
        """)

        create_template(child_path)

        assert len(asset_registry.components) == 3

    def test_get_assets_by_type(
        self, create_bird_template, create_bird_asset, create_template
    ):
        # Create template and assets
        template_file = create_bird_template("test", "<div>Test</div>")
        css_asset = create_bird_asset(template_file, ".test { color: red; }", "css")
        js_asset = create_bird_asset(template_file, "console.log('test');", "js")

        component = components.get_component("test")
        asset_registry.register(component)

        css_assets = asset_registry.get_assets(AssetType.CSS)
        js_assets = asset_registry.get_assets(AssetType.JS)

        assert len(css_assets) == 1
        assert len(js_assets) == 1
        assert Asset(Path(css_asset), AssetType.CSS) in css_assets
        assert Asset(Path(js_asset), AssetType.JS) in js_assets

    def test_register_same_component_multiple_times(
        self, create_bird_template, create_bird_asset
    ):
        # Create template and asset
        template_file = create_bird_template("test", "<div>Test</div>")
        create_bird_asset(template_file, ".test { color: red; }", "css")

        # Get the actual component through the registry
        component = components.get_component("test")

        # Register same component multiple times
        asset_registry.register(component)
        asset_registry.register(component)

        assert len(asset_registry.components) == 1
        assert len(asset_registry.get_assets(AssetType.CSS)) == 1

    def test_multiple_components_same_asset_names(
        self, create_bird_template, create_bird_asset
    ):
        # Create templates using sub_dir parameter
        template1 = create_bird_template("comp1", "<div>One</div>", sub_dir="first")
        template2 = create_bird_template("comp2", "<div>Two</div>", sub_dir="second")

        css1 = create_bird_asset(template1, ".one { color: red; }", "css")
        css2 = create_bird_asset(template2, ".two { color: blue; }", "css")

        # Get components using the full paths
        comp1 = components.get_component("first/comp1")
        comp2 = components.get_component("second/comp2")

        asset_registry.register(comp1)
        asset_registry.register(comp2)

        css_assets = asset_registry.get_assets(AssetType.CSS)
        assert len(css_assets) == 2

        asset_paths = {str(asset.path) for asset in css_assets}
        assert str(css1) in asset_paths
        assert str(css2) in asset_paths

    def test_template_inheritance_asset_ordering(
        self, create_bird_template, create_bird_asset, create_template, templates_dir
    ):
        asset_registry.clear()

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

        template = create_template(child_path)
        template.render({})

        css_assets = asset_registry.get_assets(AssetType.CSS)
        asset_paths = [str(asset.path) for asset in css_assets]

        assert str(parent_css) in asset_paths, "Parent CSS not found in assets"
        assert str(child_css) in asset_paths, "Child CSS not found in assets"
        assert asset_paths.index(str(parent_css)) < asset_paths.index(
            str(child_css)
        ), "Parent CSS should come before Child CSS"

    def test_empty_registry(self):
        # Test behavior with empty registry
        assert len(asset_registry.components) == 0
        assert len(asset_registry.get_assets(AssetType.CSS)) == 0
        assert len(asset_registry.get_assets(AssetType.JS)) == 0
