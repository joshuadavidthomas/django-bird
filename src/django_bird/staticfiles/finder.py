from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Sequence
from pathlib import Path
from typing import Any
from typing import Literal
from typing import final
from typing import overload

from django.contrib.staticfiles.finders import BaseFinder
from django.core.checks import CheckMessage
from django.core.files.storage import FileSystemStorage

from django_bird._typing import override


@final
class BirdAssetFinder(BaseFinder):
    def __init__(
        self, app_names: Sequence[str] | None = None, *args: Any, **kwargs: Any
    ) -> None:
        from django_bird.components import components

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
    def find(
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
