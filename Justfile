set unstable := true

mod copier ".just/copier.just"
mod docs ".just/documentation.just"

[private]
default:
    @just --list

[private]
fmt:
    @just --fmt
    @just copier fmt
    @just docs fmt

[private]
nox SESSION *ARGS:
    uv run nox --session "{{ SESSION }}" -- "{{ ARGS }}"

bootstrap:
    uv python install
    uv sync --frozen

coverage:
    @just nox coverage

lint:
    uv run --with pre-commit-uv pre-commit run --all-files

lock *ARGS:
    uv lock {{ ARGS }}

test *ARGS:
    @just nox test {{ ARGS }}

testall *ARGS:
    @just nox tests {{ ARGS }}

types *ARGS:
    @just nox types {{ ARGS }}
