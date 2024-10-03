set dotenv-load := true

@_default:
    just --list

# ----------------------------------------------------------------------
# DEPENDENCIES
# ----------------------------------------------------------------------

bootstrap:
    @just pup
    @just install

install:
    python -m uv pip install --editable '.[dev]'

pup:
    python -m pip install --upgrade pip uv

# ----------------------------------------------------------------------
# TESTING/TYPES
# ----------------------------------------------------------------------

nox SESSION *ARGS:
    python -m nox --session "{{ SESSION }}" -- "{{ ARGS }}"

test *ARGS:
    python -m nox --session "test" -- "{{ ARGS }}"

testall *ARGS:
    python -m nox --session "tests" -- "{{ ARGS }}"

coverage:
    python -m nox --session "coverage"

types:
    python -m nox --session "mypy"

# ----------------------------------------------------------------------
# DJANGO
# ----------------------------------------------------------------------

manage *COMMAND:
    #!/usr/bin/env python
    import sys

    try:
        from django.conf import settings
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    settings.configure(INSTALLED_APPS=["bird"])
    execute_from_command_line(sys.argv + "{{ COMMAND }}".split(" "))

alias mm := makemigrations

makemigrations *APPS:
    @just manage makemigrations {{ APPS }}

migrate *ARGS:
    @just manage migrate {{ ARGS }}

# ----------------------------------------------------------------------
# DOCS
# ----------------------------------------------------------------------

@docs-install:
    @just pup
    python -m uv pip install 'bird[docs] @ .'

@docs-serve:
    #!/usr/bin/env sh
    just _cog
    if [ -f "/.dockerenv" ]; then
        sphinx-autobuild docs docs/_build/html --host "0.0.0.0"
    else
        sphinx-autobuild docs docs/_build/html --host "localhost"
    fi

@docs-build LOCATION="docs/_build/html":
    just _cog
    sphinx-build docs {{ LOCATION }}

_cog:
    cog -r docs/development/just.md

# ----------------------------------------------------------------------
# UTILS
# ----------------------------------------------------------------------

# format justfile
fmt:
    just --fmt --unstable

# run pre-commit on all files
lint:
    python -m nox --session "lint"

# ----------------------------------------------------------------------
# COPIER
# ----------------------------------------------------------------------

# apply a copier template to project
copier-copy TEMPLATE_PATH DESTINATION_PATH=".":
    copier copy {{ TEMPLATE_PATH }} {{ DESTINATION_PATH }}

# update the project using a copier answers file
copier-update ANSWERS_FILE *ARGS:
    copier update --trust --answers-file {{ ANSWERS_FILE }} {{ ARGS }}

# loop through all answers files and update the project using copier
@copier-update-all *ARGS:
    for file in `ls .copier/`; do just copier-update .copier/$file "{{ ARGS }}"; done
