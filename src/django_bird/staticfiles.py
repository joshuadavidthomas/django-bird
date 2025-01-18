from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from django.contrib.staticfiles import finders
from django.urls import reverse

from ._typing import override


class AssetType(Enum):
    CSS = "css"
    JS = "js"

    @property
    def content_type(self):
        match self:
            case AssetType.CSS:
                return "text/css"
            case AssetType.JS:
                return "application/javascript"

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

    @property
    def url(self) -> str:
        component_name = self.path.stem
        asset_filename = self.path.name

        path = finders.find(f"django_bird/assets/{component_name}/{asset_filename}")

        return path or reverse(
            "django_bird:asset",
            kwargs={
                "component_name": component_name,
                "asset_filename": asset_filename,
            },
        )

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
