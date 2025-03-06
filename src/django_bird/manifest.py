from __future__ import annotations

import json
import logging
from pathlib import Path

from django.conf import settings

from django_bird.templates import gather_bird_tag_template_usage

logger = logging.getLogger("django_bird.assets")

# Module-level cache
_manifest_cache = None


def load_asset_manifest() -> dict[str, list[str]] | None:
    """Load asset manifest from the default location.

    Returns a simple dict mapping template paths to lists of component names.
    If the manifest cannot be loaded, returns None and falls back to runtime scanning.

    Returns:
        dict[str, list[str]] | None: Manifest data or None if not found or invalid
    """
    global _manifest_cache

    # Use cache if available
    if _manifest_cache is not None:
        return _manifest_cache

    # Try default path in STATIC_ROOT
    if hasattr(settings, "STATIC_ROOT") and settings.STATIC_ROOT:
        manifest_path = default_manifest_path()
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    manifest_data = json.load(f)
                    _manifest_cache = manifest_data
                    return manifest_data
            except json.JSONDecodeError:
                logger.warning(
                    f"Asset manifest at {manifest_path} contains invalid JSON. Falling back to registry."
                )
                return None
            except (OSError, PermissionError) as e:
                logger.warning(
                    f"Error reading asset manifest at {manifest_path}: {str(e)}. Falling back to registry."
                )
                return None

    # No manifest found, will fall back to registry
    return None


def generate_asset_manifest() -> dict[str, list[str]]:
    """Generate a manifest by scanning templates for component usage.

    Returns:
        dict[str, list[str]]: A dictionary mapping template paths to lists of component names.
    """
    # Get template-component map from Components domain
    template_component_map: dict[str, set[str]] = {}
    for template_path, component_names in gather_bird_tag_template_usage():
        # Convert Path objects to strings for JSON compatibility
        template_component_map[str(template_path)] = component_names

    # Convert to final manifest format (lists instead of sets)
    manifest: dict[str, list[str]] = {
        template: list(components)
        for template, components in template_component_map.items()
    }

    return manifest


def save_asset_manifest(
    manifest_data: dict[str, list[str]], path: Path | str, indent: int | None = None
) -> None:
    """Save asset manifest to a file.

    Args:
        manifest_data: The manifest data to save
        path: Path where to save the manifest
        indent: Optional JSON indentation level
    """
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    with open(path_obj, "w") as f:
        json.dump(manifest_data, f, indent=indent)


def default_manifest_path() -> Path:
    """Get the default manifest path.

    Returns:
        Path: The default path for the asset manifest file
    """
    if hasattr(settings, "STATIC_ROOT") and settings.STATIC_ROOT:
        return Path(settings.STATIC_ROOT) / "django_bird" / "asset-manifest.json"
    else:
        # Fallback for when STATIC_ROOT is not set
        return Path("django_bird-asset-manifest.json")
