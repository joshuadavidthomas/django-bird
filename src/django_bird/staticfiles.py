from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from django.template.backends.django import Template

from ._typing import override


class AssetType(Enum):
    CSS = "css"
    JS = "js"

    @property
    def ext(self):
        return f".{self.value}"


@dataclass(frozen=True, slots=True)
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


def get_template_assets(template: Template):
    assets: set[Asset] = set()
    template_path = Path(template.template.origin.name)
    for asset_type in AssetType:
        asset_path = template_path.with_suffix(asset_type.ext)
        if asset_path.exists():
            asset = Asset.from_path(asset_path)
            assets.add(asset)
    return assets
