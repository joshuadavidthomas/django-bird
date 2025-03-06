from __future__ import annotations

from argparse import ArgumentParser
from typing import Any
from typing import final

from django.core.management.base import BaseCommand

from django_bird._typing import override
from django_bird.manifest import default_manifest_path
from django_bird.manifest import generate_asset_manifest
from django_bird.manifest import save_asset_manifest


@final
class Command(BaseCommand):
    help: str = (
        "Generates a manifest of component usage in templates for asset optimization"
    )

    @override
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Path where the manifest file should be saved. Defaults to STATIC_ROOT/django_bird/asset-manifest.json",
        )
        parser.add_argument(
            "--pretty",
            action="store_true",
            help="Format the manifest JSON with indentation for better readability",
        )

    @override
    def handle(self, *args: Any, **options: Any) -> None:
        manifest_data = generate_asset_manifest()
        output_path = options["output"] or default_manifest_path()
        indent = 2 if options["pretty"] else None
        save_asset_manifest(manifest_data, output_path, indent=indent)
        self.stdout.write(
            self.style.SUCCESS(
                f"Asset manifest generated successfully at {output_path}"
            )
        )
