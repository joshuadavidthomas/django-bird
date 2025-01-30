from __future__ import annotations

from collections.abc import Generator
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from typing import TypeVar


def get_files_from_dirs(
    dirs: Iterable[Path],
    pattern: str = "*",
) -> Generator[tuple[Path, Path], Any, None]:
    for dir in dirs:
        for path in dir.rglob(pattern):
            if path.is_file():
                yield path, dir


Item = TypeVar("Item")


def unique_ordered(items: Iterable[Item]) -> list[Item]:
    return list(dict.fromkeys(items))
