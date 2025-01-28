from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Literal
from typing import final
from typing import overload

from django.contrib.staticfiles import finders
from django.contrib.staticfiles.finders import BaseFinder
from django.core.checks import CheckMessage
from django.core.files.storage import FileSystemStorage
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
    def absolute_path(self):
        return self.path.resolve()

    @property
    def relative_path(self):
        return self.path.relative_to(self.template_dir)

    @property
    def storage(self):
        return FileSystemStorage(location=str(self.template_dir))

    @property
    def template_dir(self):
        template_dir = self.path.parent
        while len(template_dir.parts) > 1 and template_dir.parts[-1] != "bird":
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
    def from_path(cls, path: Path) -> Asset:
        match path.suffix.lower():
            case ".css":
                asset_type = AssetType.CSS
            case ".js":
                asset_type = AssetType.JS
            case _:
                raise ValueError(f"Unknown asset type for path: {path}")
        return cls(path=path, type=asset_type)


@final
class BirdAssetFinder(BaseFinder):
    def __init__(
        self, app_names: Sequence[str] | None = None, *args: Any, **kwargs: Any
    ) -> None:
        from .components import components

        self.components = components
        super().__init__(*args, **kwargs)

    @override
    def check(self, **kwargs: Any) -> list[CheckMessage]:
        return []

    @overload
    def find(self, path: str, all: Literal[False] = False) -> str | None: ...
    @overload
    def find(self, path: str, all: Literal[True]) -> list[str]: ...
    @override
    def find(self, path: str, all: bool = False) -> str | list[str] | None:
        """
        Given a relative file path, return the absolute path(s) where it can be found.
        """
        self.components.discover_components()

        matches: list[str] = []
        path_obj = Path(path)

        for asset in self.components.get_assets():
            if path_obj == asset.relative_path:
                matched_path = str(asset.absolute_path)
            elif asset.relative_path.is_relative_to(path_obj):
                matched_path = str(path_obj.resolve())
            else:
                continue

            if not all:
                return matched_path
            matches.append(matched_path)

        return matches

    @override
    def list(
        self, ignore_patterns: Iterable[str] | None
    ) -> Iterable[tuple[str, FileSystemStorage]]:
        """
        Return (relative_path, storage) pairs for all assets.
        """
        self.components.discover_components()

        for asset in self.components.get_assets():
            if ignore_patterns and any(
                asset.relative_path.match(pattern) for pattern in set(ignore_patterns)
            ):
                continue
            yield str(asset.relative_path), asset.storage
