from __future__ import annotations

import os
from pathlib import Path

import nox

nox.options.default_venv_backend = "uv|virtualenv"
nox.options.reuse_existing_virtualenvs = True

PY310 = "3.10"
PY311 = "3.11"
PY312 = "3.12"
PY313 = "3.13"
PY_VERSIONS = [PY310, PY311, PY312, PY313]
PY_DEFAULT = PY_VERSIONS[0]
PY_LATEST = PY_VERSIONS[-1]

DJ42 = "4.2"
DJ50 = "5.0"
DJ51 = "5.1"
DJMAIN = "main"
DJMAIN_MIN_PY = PY310
DJ_VERSIONS = [DJ42, DJ50, DJ51, DJMAIN]
DJ_LTS = [DJ42]
DJ_DEFAULT = DJ_LTS[0]
DJ_LATEST = DJ_VERSIONS[-2]


def version(ver: str) -> tuple[int, ...]:
    """Convert a string version to a tuple of ints, e.g. "3.10" -> (3, 10)"""
    return tuple(map(int, ver.split(".")))


def should_skip(python: str, django: str) -> bool:
    """Return True if the test should be skipped"""

    if django == DJMAIN and version(python) < version(DJMAIN_MIN_PY):
        # Django main requires Python 3.10+
        return True

    if django == DJ50 and version(python) < version(PY310):
        # Django 5.0 requires Python 3.10+
        return True

    return False


@nox.session
def test(session):
    session.notify(f"tests(python='{PY_DEFAULT}', django='{DJ_DEFAULT}')")


@nox.session
@nox.parametrize(
    "python,django",
    [
        (python, django)
        for python in PY_VERSIONS
        for django in DJ_VERSIONS
        if not should_skip(python, django)
    ],
)
def tests(session, django):
    session.install("django-bird[dev] @ .")

    if django == DJMAIN:
        session.install(
            "django @ https://github.com/django/django/archive/refs/heads/main.zip"
        )
    else:
        session.install(f"django=={django}")

    command = ["uv", "run", "pytest"]
    if session.posargs:
        command.append(*session.posargs)
    session.run(*command)


@nox.session
def coverage(session):
    session.install("django-bird[dev] @ .")
    session.run("python", "-m", "pytest", "--cov")

    try:
        summary = os.environ["GITHUB_STEP_SUMMARY"]
        with Path(summary).open("a") as output_buffer:
            output_buffer.write("")
            output_buffer.write("### Coverage\n\n")
            output_buffer.flush()
            session.run(
                "python",
                "-m",
                "coverage",
                "report",
                "--skip-covered",
                "--skip-empty",
                "--format=markdown",
                stdout=output_buffer,
            )
    except KeyError:
        session.run(
            "python", "-m", "coverage", "html", "--skip-covered", "--skip-empty"
        )

    session.run("python", "-m", "coverage", "report")


@nox.session
def lint(session):
    session.install("django-bird[lint] @ .")
    session.run("python", "-m", "pre_commit", "run", "--all-files")


@nox.session
def mypy(session):
    session.install("django-bird[dev,types] @ .")
    session.run("python", "-m", "mypy", ".")
