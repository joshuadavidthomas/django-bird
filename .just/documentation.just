set unstable := true

justfile := justfile_directory() + "/.just/documentation.just"

[private]
default:
    @just --list --justfile {{ justfile }}

[private]
fmt:
    @just --fmt --justfile {{ justfile }}

# Build documentation using Sphinx
[no-cd]
build LOCATION="docs/_build/html": cog
    uv run --extra docs sphinx-build docs {{ LOCATION }}

# Serve documentation locally
[no-cd]
serve PORT="8000": cog
    #!/usr/bin/env sh
    HOST="localhost"
    if [ -f "/.dockerenv" ]; then
        HOST="0.0.0.0"
    fi
    uv run --extra docs sphinx-autobuild docs docs/_build/html --host "$HOST" --port {{ PORT }}

[no-cd]
[private]
cog:
    uv run --extra docs cog -r docs/development/just.md
