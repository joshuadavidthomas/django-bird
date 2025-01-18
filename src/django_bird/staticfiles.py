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

    @classmethod
    def from_tag_name(cls, tag_name: str):
        try:
            asset_type = tag_name.split(":")[1]
            match asset_type:
                case "css":
                    return cls.CSS
                case "js":
                    return cls.JS
                case _:
                    raise ValueError(f"Unknown asset type: {asset_type}")
        except IndexError as e:
            raise ValueError(f"Invalid tag name: {tag_name}") from e


@dataclass(frozen=True, slots=True)
class Asset:
    path: Path
    type: AssetType

    @override
    def __hash__(self) -> int:
        return hash((str(self.path), self.type))

    def exists(self) -> bool:
        return self.path.exists()

    def render(self):
        match self.type:
            case AssetType.CSS:
                return f'<link rel="stylesheet" href="{self.url}">'
            case AssetType.JS:
                return f'<script src="{self.url}"></script>'

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
