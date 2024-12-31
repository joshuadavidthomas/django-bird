from __future__ import annotations

from pathlib import Path

import pytest

from django_bird.staticfiles import Asset
from django_bird.staticfiles import AssetType


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
