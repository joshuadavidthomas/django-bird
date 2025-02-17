from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from pluggy import HookspecMarker

if TYPE_CHECKING:
    from django_bird.staticfiles import Asset
    from django_bird.staticfiles import AssetType

hookspec = HookspecMarker("django_bird")


@hookspec
def collect_component_assets(template_path: Path) -> Iterable[Asset]:
    """Collect all assets associated with a component.

    This hook is called for each component template to gather its associated static assets.
    Implementations should scan for and return any CSS, JavaScript or other static files
    that belong to the component and return a list/set/other iterable of `Asset` objects.
    """


@hookspec
def get_template_directories() -> list[Path]:
    """Return a list of all directories containing templates for a project.

    This hook allows plugins to provide additional template directories beyond the default
    Django template directories. Implementations should return a list of Path objects
    pointing to directories that contain Django templates.

    The template directories returned by this hook will be used by django-bird to discover
    components and their associated templates.
    """


@hookspec
def register_asset_types(register_type: Callable[[AssetType], None]) -> None:
    """Register a new type of asset.

    This hook allows plugins to register additional asset types beyond the default CSS
    and JS types. Each asset type defines how static assets should be rendered in HTML,
    what file extension it uses, and what django-bird asset templatetag it should be
    rendered with.
    """
