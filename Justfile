set dotenv-load := true

@_default:
    just --list

benchmark:
    #!./.venv/bin/python
    from __future__ import annotations

    import timeit

    from django_bird.compiler import Compiler


    def benchmark_compilation(template_string):
        compiler = Compiler()

        def compile_template():
            compiler.compile(template_string)

        number = 1000  # number of times to run the test
        time_taken = timeit.timeit(compile_template, number=number)
        print(f"Average time to compile: {time_taken/number:.6f} seconds")

    small_template = "<bird:div>Hello, World!</bird:div>"
    medium_template = (
        "<bird:div><bird:p>Paragraph 1</bird:p><bird:p>Paragraph 2</bird:p></bird:div>"
    )
    large_template = "<bird:div>" + "<bird:p>Paragraph</bird:p>" * 1000 + "</bird:div>"

    benchmark_compilation(small_template)
    benchmark_compilation(medium_template)
    benchmark_compilation(large_template)

profile:
    #!./.venv/bin/python
    from __future__ import annotations

    import cProfile
    import pstats

    from django_bird.compiler import Compiler


    def compile_template(template):
        compiler = Compiler()
        return compiler.compile(template)

    large_template = "<bird:div>" + "<bird:p>Paragraph</bird:p>" * 1000 + "</bird:div>"

    cProfile.runctx(
        "compile_template(large_template)", globals(), locals(), "compiler_stats"
    )

    p = pstats.Stats("compiler_stats")
    p.strip_dirs().sort_stats("cumulative").print_stats(20)

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

    settings.configure(INSTALLED_APPS=["django_bird"])
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
