from __future__ import annotations

import hashlib
import json
import logging
from enum import Enum
from pathlib import Path

from django.conf import settings

from django_bird.templates import gather_bird_tag_template_usage

logger = logging.getLogger(__name__)

_manifest_cache = None


class PathPrefix(str, Enum):
    """Path prefixes used for normalizing template paths."""

    PKG = "pkg:"
    APP = "app:"
    EXT = "ext:"

    def prepend_to(self, path: str) -> str:
        """Generate a prefixed path string by prepending this prefix to a path.

        Args:
            path: The path to prefix

        Returns:
            str: A string with this prefix and the path
        """
        return f"{self.value}{path}"

    @classmethod
    def has_prefix(cls, path: str) -> bool:
        """Check if a path already has one of the recognized prefixes.

        Args:
            path: The path to check

        Returns:
            bool: True if the path starts with any of the recognized prefixes
        """
        return any(path.startswith(prefix.value) for prefix in cls)


def normalize_path(path: str) -> str:
    """Normalize a template path to remove system-specific information.

    Args:
        path: The template path to normalize

    Returns:
        str: A normalized path without system-specific details
    """
    if PathPrefix.has_prefix(path):
        return path

    if "site-packages" in path:
        parts = path.split("site-packages/")
        if len(parts) > 1:
            return PathPrefix.PKG.prepend_to(parts[1])

    if hasattr(settings, "BASE_DIR") and settings.BASE_DIR:  # type: ignore[misc]
        base_dir = Path(settings.BASE_DIR).resolve()  # type: ignore[misc]
        abs_path = Path(path).resolve()
        try:
            if str(abs_path).startswith(str(base_dir)):
                rel_path = abs_path.relative_to(base_dir)
                return PathPrefix.APP.prepend_to(str(rel_path))
        except ValueError:
            # Path is not relative to BASE_DIR
            pass

    if path.startswith("/"):
        hash_val = hashlib.md5(path.encode()).hexdigest()[:8]
        filename = Path(path).name
        return PathPrefix.EXT.prepend_to(f"{hash_val}/{filename}")

    # Return as is if it's already a relative path
    return path


def load_asset_manifest() -> dict[str, list[str]] | None:
    """Load asset manifest from the default location.

    Returns a simple dict mapping template paths to lists of component names.
    If the manifest cannot be loaded, returns None and falls back to runtime scanning.

    Returns:
        dict[str, list[str]] | None: Manifest data or None if not found or invalid
    """
    global _manifest_cache

    if _manifest_cache is not None:
        return _manifest_cache

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
    template_component_map: dict[str, set[str]] = {}

    for template_path, component_names in gather_bird_tag_template_usage():
        # Convert Path objects to strings for JSON and normalize
        original_path = str(template_path)
        normalized_path = normalize_path(original_path)
        template_component_map[normalized_path] = component_names

    manifest: dict[str, list[str]] = {
        template: sorted(list(components))
        for template, components in template_component_map.items()
    }

    return manifest


def save_asset_manifest(manifest_data: dict[str, list[str]], path: Path | str) -> None:
    """Save asset manifest to a file.

    Args:
        manifest_data: The manifest data to save
        path: Path where to save the manifest
    """
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    with open(path_obj, "w") as f:
        json.dump(manifest_data, f, indent=2)


def default_manifest_path() -> Path:
    """Get the default manifest path.

    Returns:
        Path: The default path for the asset manifest file
    """
    if hasattr(settings, "STATIC_ROOT") and settings.STATIC_ROOT:
        return Path(settings.STATIC_ROOT) / "django_bird" / "manifest.json"
    else:
        # Fallback for when STATIC_ROOT is not set
        return Path("django_bird-asset-manifest.json")
