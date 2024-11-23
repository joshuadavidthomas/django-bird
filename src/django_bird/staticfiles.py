from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from enum import IntEnum
from pathlib import Path

from ._typing import override


class AssetType(IntEnum):
    CSS = 1
    JS = 2


class Registry(ABC):
    asset_type: AssetType

    def __init__(self):
        self._assets: set[Path] = set()
        self._processed_assets: dict[str, str] = {}

    def register(self, path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"Asset file not found: {path}")
        self._assets.add(path)

    def get_processed_content(self, path: Path) -> str:
        if str(path) not in self._processed_assets:
            self._processed_assets[str(path)] = self._process_content(path)
        return self._processed_assets[str(path)]

    @abstractmethod
    def _process_content(self, path: Path) -> str: ...

    def get_all_assets(self) -> str:
        return "\n".join(
            self.get_processed_content(path) for path in sorted(self._assets)
        )

    def clear(self) -> None:
        self._assets.clear()
        self._processed_assets.clear()


class CSSRegistry(Registry):
    asset_type = AssetType.CSS

    @override
    def _process_content(self, path: Path) -> str:
        with open(path) as f:
            content = f.read()
        return content

    @override
    def get_all_assets(self) -> str:
        css_content = super().get_all_assets()
        return f'<style type="text/css">\n{css_content}\n</style>'


class JSRegistry(Registry):
    asset_type = AssetType.JS

    @override
    def _process_content(self, path: Path) -> str:
        with open(path) as f:
            content = f.read()
        return content

    @override
    def get_all_assets(self) -> str:
        js_content = super().get_all_assets()
        return f'<script type="text/javascript">\n{js_content}\n</script>'


js_registry = JSRegistry()
css_registry = CSSRegistry()
