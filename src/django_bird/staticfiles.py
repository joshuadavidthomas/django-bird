from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.html import format_html_join
from django.utils.safestring import SafeString

from ._typing import override


class AssetType(IntEnum):
    CSS = 1
    JS = 2


@dataclass(frozen=True)
class Asset:
    path: Path
    type: AssetType

    @override
    def __hash__(self) -> int:
        return hash((str(self.path), self.type))

    def exists(self) -> bool:
        return self.path.exists()

    @classmethod
    def from_path(cls, path: Path) -> Asset:
        match path.suffix.lower():
            case ".css":
                asset_type = AssetType.CSS
            case ".js":
                asset_type = AssetType.JS
            case _:
                raise ValueError(f"Unknown asset type for path: {path}")
        return cls(path=path, type=asset_type)


class Registry:
    def __init__(self) -> None:
        self.assets: set[Asset] = set()

    def register(self, asset: Asset | Path) -> None:
        if isinstance(asset, Path):
            asset = Asset.from_path(asset)

        if not asset.exists():
            raise FileNotFoundError(f"Asset file not found: {asset.path}")

        self.assets.add(asset)

    def clear(self) -> None:
        self.assets.clear()

    def get_assets(self, asset_type: AssetType) -> list[Asset]:
        assets = [asset for asset in self.assets if asset.type == asset_type]
        return self.sort_assets(assets)

    def sort_assets(
        self,
        assets: list[Asset],
        *,
        key: Callable[[Asset], str] = lambda a: str(a.path),
    ) -> list[Asset]:
        return sorted(assets, key=key)

    def get_format_string(self, asset_type: AssetType) -> str:
        match asset_type:
            case AssetType.CSS:
                return '<link rel="stylesheet" href="{}" type="text/css">'
            case AssetType.JS:
                return '<script src="{}" type="text/javascript">'

    def render(self, asset_type: AssetType) -> SafeString:
        assets = self.get_assets(asset_type)

        if not assets:
            return format_html("")

        return format_html_join(
            "\n",
            self.get_format_string(asset_type),
            ((static(str(asset.path)),) for asset in assets),
        )


registry = Registry()
