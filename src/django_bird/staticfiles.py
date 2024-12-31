from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

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
