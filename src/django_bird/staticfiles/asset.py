from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from django.contrib.staticfiles import finders
from django.core.files.storage import FileSystemStorage
from django.urls import reverse

from django_bird._typing import override
from django_bird.apps import DjangoBirdAppConfig
from django_bird.conf import app_settings


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
    def absolute_path(self):
        return self.path.resolve()

    @property
    def relative_path(self):
        return self.path.relative_to(self.template_dir)

    @property
    def storage(self):
        storage = FileSystemStorage(location=str(self.template_dir))
        storage.prefix = DjangoBirdAppConfig.label  # type: ignore[attr-defined]
        return storage

    @property
    def template_dir(self):
        template_dir = self.path.parent
        component_dirs = app_settings.get_component_directory_names()
        while (
            len(template_dir.parts) > 1 and template_dir.parts[-1] not in component_dirs
        ):
            template_dir = template_dir.parent
        return template_dir.parent

    @property
    def url(self) -> str:
        path = finders.find(str(self.relative_path))
        return path or reverse(
            "django_bird:asset",
            kwargs={
                "component_name": self.path.stem,
                "asset_filename": self.path.name,
            },
        )

    @classmethod
    def from_path(cls, path: Path, asset_type: AssetType):
        asset_path = path.with_suffix(asset_type.ext)
        if asset_path.exists():
            return cls(path=asset_path, type=asset_type)
        return None
