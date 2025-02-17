from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from pluggy import HookspecMarker

if TYPE_CHECKING:
    from django_bird.staticfiles import Asset
    from django_bird.staticfiles import AssetTypes

hookspec = HookspecMarker("django_bird")


@hookspec
def collect_component_assets(template_path: Path) -> Iterable[Asset]:
    """Collect all assets associated with a component.

    This hook is called for each component template to gather its associated static assets.
    Implementations should scan for and return any CSS, JavaScript or other static files
    that belong to the component and return a list/set/other iterable of `Asset` objects.
    """


@hookspec
def register_asset_types(asset_types: AssetTypes) -> None:
    """Register a new type of asset.

    This hook allows plugins to register additional asset types beyond the default CSS
    and JS types. Each asset type defines how static assets should be rendered in HTML,
    what file extension it uses, and what django-bird asset templatetag it should be
    rendered with.
    """
