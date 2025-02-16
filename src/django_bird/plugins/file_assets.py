from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from django_bird import hookimpl
from django_bird.staticfiles import Asset
from django_bird.staticfiles import AssetType


def find_component_asset(path: Path, asset_type: AssetType) -> Asset | None:
    asset_path = path.with_suffix(asset_type.ext)
    if asset_path.exists():
        return Asset(path=asset_path, type=asset_type)
    return None


@hookimpl
def collect_component_assets(template_path: Path) -> Iterable[Asset]:
    assets: list[Asset] = []
    for asset_type in AssetType:
        if asset := find_component_asset(template_path, asset_type):
            assets.append(asset)
    return assets
