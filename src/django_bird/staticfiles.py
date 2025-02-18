from __future__ import annotations

from collections.abc import Callable
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
from django.contrib.staticfiles.storage import StaticFilesStorage
from django.core.checks import CheckMessage
from django.core.files.storage import FileSystemStorage

from django_bird import hookimpl

from ._typing import override
from .apps import DjangoBirdAppConfig
from .conf import app_settings
from .templates import get_component_directories
from .templatetags.tags.asset import AssetTag


class AssetElement(Enum):
    STYLESHEET = "stylesheet"
    SCRIPT = "script"


@dataclass(frozen=True, slots=True)
class AssetType:
    element: AssetElement
    extension: str
    tag: AssetTag

    @property
    def suffix(self):
        return f".{self.extension}"


CSS = AssetType(
    element=AssetElement.STYLESHEET,
    extension="css",
    tag=AssetTag.CSS,
)
JS = AssetType(
    element=AssetElement.SCRIPT,
    extension="js",
    tag=AssetTag.JS,
)


@final
class AssetTypes:
    def __init__(self):
        self.types: set[AssetType] = set()

    def is_known_type(self, path: Path) -> bool:
        return any(path.suffix == asset_type.suffix for asset_type in self.types)

    def register_type(self, asset_type: AssetType) -> None:
        self.types.add(asset_type)

    def reset(self) -> None:
        self.types.clear()


asset_types = AssetTypes()


@hookimpl
def register_asset_types(register_type: Callable[[AssetType], None]):
    register_type(CSS)
    register_type(JS)


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
        if self.url is None:
            return ""

        match self.type.element:
            case AssetElement.STYLESHEET:
                return f'<link rel="stylesheet" href="{self.url}">'
            case AssetElement.SCRIPT:
                return f'<script src="{self.url}"></script>'

    @property
    def absolute_path(self):
        return self.path.resolve()

    @property
    def relative_path(self):
        return self.path.relative_to(self.template_dir)

    @property
    def storage(self):
        return BirdAssetStorage(
            location=str(self.template_dir), prefix=DjangoBirdAppConfig.label
        )

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
    def url(self) -> str | None:
        static_path = finders.find(str(self.relative_path))
        if static_path is None:
            return None
        static_relative_path = Path(static_path).relative_to(self.template_dir)
        return self.storage.url(str(static_relative_path))


@hookimpl
def collect_component_assets(template_path: Path) -> Iterable[Asset]:
    assets: list[Asset] = []
    for asset_type in asset_types.types:
        asset_path = template_path.with_suffix(asset_type.suffix)
        if asset_path.exists():
            assets.append(Asset(path=asset_path, type=asset_type))
    return assets


@final
class BirdAssetStorage(StaticFilesStorage):
    def __init__(self, *args: Any, prefix: str, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.prefix = prefix


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

    # Django 5.2 changed the argument from `find` to `find_all`, but django-stubs
    # (as of the time of this commit) hasn't been updated to reflect this, hence the
    # type ignore
    @overload  # type: ignore[override]
    def find(self, path: str, *, all: Literal[False] = False) -> str | None: ...
    @overload
    def find(self, path: str, *, all: Literal[True]) -> list[str]: ...
    @overload
    def find(self, path: str, *, find_all: Literal[False] = False) -> str | None: ...
    @overload
    def find(self, path: str, *, find_all: Literal[True]) -> list[str]: ...
    @override
    def find(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        path: str,
        all: bool = False,
        find_all: bool | None = None,
    ) -> str | list[str] | None:
        """
        Given a relative file path, return the absolute path(s) where it can be found.
        """
        if find_all is None:
            find_all = all

        path_obj = Path(path)

        # check if asset type is registered and check if it's a file
        # (allow directories to pass through)
        if not asset_types.is_known_type(path_obj) and path_obj.suffix:
            return []

        path_base_dir = path_obj.parts[0]
        matches: list[str] = []

        for component_dir in get_component_directories():
            if component_dir.name == path_base_dir:
                asset_path = component_dir / path_obj.relative_to(path_base_dir)
                if asset_path.exists():
                    matched_path = str(asset_path)
                    if not find_all:
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
