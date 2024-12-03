from __future__ import annotations

from pathlib import Path

import pytest

from django_bird.staticfiles import Asset
from django_bird.staticfiles import AssetType
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
