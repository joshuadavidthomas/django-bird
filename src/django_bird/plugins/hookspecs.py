from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from pluggy import HookspecMarker

from django_bird.staticfiles import Asset

hookspec = HookspecMarker("django_bird")


@hookspec
def collect_component_assets(template_path: Path) -> Iterable[Asset]:
    """Collect all assets associated with a component."""
