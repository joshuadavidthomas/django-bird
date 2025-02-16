from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from pluggy import HookspecMarker

from django_bird.staticfiles import Asset

hookspec = HookspecMarker("django_bird")


@hookspec
def collect_component_assets(template_path: Path) -> Iterable[Asset]:
    """Collect all assets associated with a component.

    This hook is called for each component template to gather its associated static assets.
    Implementations should scan for and return any CSS, JavaScript or other static files
    that belong to the component and return a list/set/other iterable of `Asset` objects.
    """
