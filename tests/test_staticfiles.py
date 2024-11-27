from __future__ import annotations

from pathlib import Path

import pytest
from django.utils.safestring import SafeString

from django_bird.staticfiles import Asset
from django_bird.staticfiles import AssetType
from django_bird.staticfiles import registry


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


class TestRegistry:
    @pytest.fixture
    def registry(self):
        registry.clear()
        yield registry
        registry.clear()

    def test_register_asset(self, registry, tmp_path):
        css_file = tmp_path / "test.css"
        css_file.touch()
        asset = Asset(css_file, AssetType.CSS)

        registry.register(asset)

        assert asset in registry.assets

    def test_register_path(self, registry, tmp_path):
        css_file = tmp_path / "test.css"
        css_file.touch()

        registry.register(css_file)

        assert len(registry.assets) == 1
        assert next(iter(registry.assets)).path == css_file

    def test_register_missing_file(self, registry, tmp_path):
        missing_file = tmp_path / "missing.css"

        with pytest.raises(FileNotFoundError):
            registry.register(missing_file)

    def test_clear(self, registry, tmp_path):
        css_file = tmp_path / "test.css"
        css_file.touch()
        js_file = tmp_path / "test.js"
        js_file.touch()
        registry.register(Asset(css_file, AssetType.CSS))
        registry.register(Asset(js_file, AssetType.JS))

        assert len(registry.assets) == 2

        registry.clear()

        assert len(registry.assets) == 0

    @pytest.mark.parametrize("asset_type", [AssetType.CSS, AssetType.JS])
    def test_get_assets(self, asset_type, registry):
        css_asset = Asset(Path("test.css"), AssetType.CSS)
        js_asset = Asset(Path("test.js"), AssetType.JS)

        registry.assets = {css_asset, js_asset}

        assets = registry.get_assets(asset_type)

        assert len(assets) == 1
        assert all(asset.type == asset_type for asset in assets)

    @pytest.mark.parametrize(
        "assets,sort_key,expected",
        [
            (
                [
                    Asset(Path("test/a.css"), AssetType.CSS),
                    Asset(Path("test/b.css"), AssetType.CSS),
                ],
                None,
                ["test/a.css", "test/b.css"],
            ),
            (
                [
                    Asset(Path("test/b.css"), AssetType.CSS),
                    Asset(Path("other/a.css"), AssetType.CSS),
                ],
                lambda a: a.path.name,
                ["other/a.css", "test/b.css"],
            ),
            ([], None, []),
            (
                [Asset(Path("test.css"), AssetType.CSS)],
                None,
                ["test.css"],
            ),
        ],
    )
    def test_sort_assets(self, assets, sort_key, expected, registry):
        kwargs = {}
        if sort_key is not None:
            kwargs["key"] = sort_key

        sorted_assets = registry.sort_assets(assets, **kwargs)

        assert [str(a.path) for a in sorted_assets] == expected

    @pytest.mark.parametrize(
        "asset_type,expected",
        [
            (AssetType.CSS, '<link rel="stylesheet" href="{}" type="text/css">'),
            (AssetType.JS, '<script src="{}" type="text/javascript">'),
        ],
    )
    def test_get_format_string(self, asset_type, expected, registry):
        assert registry.get_format_string(asset_type) == expected

    @pytest.mark.parametrize(
        "assets,asset_type,expected",
        [
            (set(), AssetType.CSS, ""),
            (
                {Asset(Path("test.css"), AssetType.CSS)},
                AssetType.CSS,
                ('rel="stylesheet"', 'href="test.css"'),
            ),
            (
                {Asset(Path("test.js"), AssetType.JS)},
                AssetType.JS,
                ('<script src="test.js"',),
            ),
            (
                {
                    Asset(Path("a.css"), AssetType.CSS),
                    Asset(Path("b.css"), AssetType.CSS),
                },
                AssetType.CSS,
                ('stylesheet" href="a.css"', 'stylesheet" href="b.css"'),
            ),
        ],
    )
    def test_render(self, assets, asset_type, expected, registry):
        registry.assets = assets

        rendered = registry.render(asset_type)

        assert isinstance(rendered, SafeString)
        for content in expected:
            assert content in rendered
