from __future__ import annotations

import json
from pathlib import Path

import pytest
from django.test import override_settings

from django_bird.manifest import generate_asset_manifest
from django_bird.manifest import load_asset_manifest
from django_bird.manifest import save_asset_manifest


@pytest.fixture(autouse=True)
def reset_manifest_cache():
    """Reset the manifest cache before and after each test."""
    # Access and reset the private module-level cache variable
    import django_bird.manifest

    django_bird.manifest._manifest_cache = None
    yield
    django_bird.manifest._manifest_cache = None


def test_load_asset_manifest_with_asset_manifest_setting(tmp_path):
    """Test loading manifest from a file specified in ASSET_MANIFEST setting."""
    # Create test manifest data
    test_manifest_data = {
        "/path/to/template1.html": ["button", "card"],
        "/path/to/template2.html": ["accordion", "tab"],
    }

    # Create manifest file
    manifest_path = tmp_path / "test-manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(test_manifest_data, f)

    # Test loading with ASSET_MANIFEST setting
    with override_settings(DJANGO_BIRD={"ASSET_MANIFEST": str(manifest_path)}):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest == test_manifest_data


def test_load_asset_manifest_nonexistent():
    """Test loading manifest from a nonexistent file."""
    with override_settings(
        DJANGO_BIRD={"ASSET_MANIFEST": "/nonexistent/path/manifest.json"}
    ):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest is None


def test_load_asset_manifest_invalid_json(tmp_path):
    """Test handling of invalid JSON in manifest file."""
    invalid_json_file = tmp_path / "invalid.json"
    invalid_json_file.write_text("{ this is not valid JSON }")

    with override_settings(DJANGO_BIRD={"ASSET_MANIFEST": str(invalid_json_file)}):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest is None


def test_load_asset_manifest_from_static_root(tmp_path):
    """Test loading manifest from the default STATIC_ROOT path."""
    # Create test manifest data
    test_manifest_data = {
        "/path/to/template1.html": ["button", "card"],
        "/path/to/template2.html": ["accordion", "tab"],
    }

    # Create STATIC_ROOT structure
    static_root = tmp_path / "static"
    static_root.mkdir()
    django_bird_dir = static_root / "django_bird"
    django_bird_dir.mkdir()

    # Create manifest file in default location
    manifest_path = django_bird_dir / "asset-manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(test_manifest_data, f)

    # Test loading with STATIC_ROOT setting but no ASSET_MANIFEST
    with override_settings(STATIC_ROOT=str(static_root), DJANGO_BIRD={}):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest == test_manifest_data


def test_generate_asset_manifest(tmp_path, templates_dir, registry):
    """Test generating a manifest from a real template scan."""
    # Create test templates with components
    template1 = templates_dir / "test_manifest1.html"
    template1.write_text("""
    <html>
    <head>
        <title>Test</title>
    </head>
    <body>
        {% bird button %}Button{% endbird %}
        {% bird card %}Card{% endbird %}
    </body>
    </html>
    """)

    template2 = templates_dir / "test_manifest2.html"
    template2.write_text("""
    <html>
    <head>
        <title>Test</title>
    </head>
    <body>
        {% bird accordion %}Accordion{% endbird %}
        {% bird tab %}Tab{% endbird %}
    </body>
    </html>
    """)

    # Create the components
    from tests.utils import TestComponent

    TestComponent(name="button", content="<button>{{ slot }}</button>").create(
        templates_dir
    )
    TestComponent(name="card", content="<div class='card'>{{ slot }}</div>").create(
        templates_dir
    )
    TestComponent(
        name="accordion", content="<div class='accordion'>{{ slot }}</div>"
    ).create(templates_dir)
    TestComponent(name="tab", content="<div class='tab'>{{ slot }}</div>").create(
        templates_dir
    )

    # Use the registry fixture to discover components
    registry.discover_components()

    # Generate the manifest
    manifest = generate_asset_manifest()

    # Check that our test templates are in the manifest
    # We don't know the exact paths, so we need to check differently
    all_keys = list(manifest.keys())
    template1_key = [k for k in all_keys if str(template1) in k][0]
    template2_key = [k for k in all_keys if str(template2) in k][0]

    # Verify component names in template1
    assert sorted(manifest[template1_key]) == sorted(["button", "card"])

    # Verify component names in template2
    assert sorted(manifest[template2_key]) == sorted(["accordion", "tab"])


def test_save_and_load_asset_manifest(tmp_path):
    """Test saving and loading a manifest."""
    # Create test manifest data
    test_manifest_data = {
        "/path/to/template1.html": ["button", "card"],
        "/path/to/template2.html": ["accordion", "tab"],
    }

    # Create output path
    output_path = tmp_path / "test-manifest.json"

    # Save manifest
    save_asset_manifest(test_manifest_data, output_path)

    # Verify file exists
    assert output_path.exists()

    # Load and verify contents directly
    with open(output_path) as f:
        loaded_data = json.load(f)

    assert loaded_data == test_manifest_data

    # Also verify using the load_asset_manifest function
    with override_settings(DJANGO_BIRD={"ASSET_MANIFEST": str(output_path)}):
        loaded_manifest = load_asset_manifest()
        assert loaded_manifest == test_manifest_data


def test_default_manifest_path():
    """Test the default_manifest_path function."""
    from django_bird.manifest import default_manifest_path

    # Test with STATIC_ROOT
    with override_settings(STATIC_ROOT="/path/to/static"):
        path = default_manifest_path()
        assert path == Path("/path/to/static/django_bird/asset-manifest.json")

    # Test without STATIC_ROOT
    with override_settings(STATIC_ROOT=None):
        path = default_manifest_path()
        assert path == Path("django_bird-asset-manifest.json")
