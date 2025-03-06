from __future__ import annotations

from django.core.management.base import BaseCommand

from django_bird.manifest import default_manifest_path
from django_bird.manifest import generate_asset_manifest
from django_bird.manifest import save_asset_manifest


class Command(BaseCommand):
    help = "Generates a manifest of component usage in templates for asset optimization"

    def add_arguments(self, parser):
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

    def handle(self, *args, **options):
        # Generate the manifest
        manifest_data = generate_asset_manifest()

        # Determine output path
        output_path = options["output"] or default_manifest_path()

        # Use pretty printing if requested, otherwise compact
        indent = 2 if options["pretty"] else None

        # Save the manifest
        save_asset_manifest(manifest_data, output_path, indent=indent)

        self.stdout.write(
            self.style.SUCCESS(
                f"Asset manifest generated successfully at {output_path}"
            )
        )
