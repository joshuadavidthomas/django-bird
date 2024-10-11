from __future__ import annotations

import json
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
DJ_LTS = [
    version for version in DJ_VERSIONS if version.endswith(".2") and version != DJMAIN
]
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

    if django == DJ51 and version(python) < version(PY310):
        # Django 5.1 requires Python 3.10+
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
    session.run_install(
        "uv",
        "sync",
        "--extra",
        "tests",
        "--frozen",
        "--inexact",
        "--no-install-package",
        "django",
        "--python",
        session.python,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    if django == DJMAIN:
        session.install(
            "django @ https://github.com/django/django/archive/refs/heads/main.zip"
        )
    else:
        session.install(f"django=={django}")

    command = ["python", "-m", "pytest"]
    if session.posargs and all(arg for arg in session.posargs):
        command.append(*session.posargs)
    session.run(*command)


@nox.session
def coverage(session):
    session.run_install(
        "uv",
        "sync",
        "--extra",
        "tests",
        "--frozen",
        "--python",
        PY_DEFAULT,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    try:
        session.run("python", "-m", "pytest", "--cov", "--cov-report=")
    finally:
        report_cmd = ["python", "-m", "coverage", "report"]
        session.run(*report_cmd)

        if summary := os.getenv("GITHUB_STEP_SUMMARY"):
            report_cmd.extend(["--skip-covered", "--skip-empty", "--format=markdown"])

            with Path(summary).open("a") as output_buffer:
                output_buffer.write("")
                output_buffer.write("### Coverage\n\n")
                output_buffer.flush()
                session.run(*report_cmd, stdout=output_buffer)
        else:
            session.run(
                "python", "-m", "coverage", "html", "--skip-covered", "--skip-empty"
            )


@nox.session
def types(session):
    session.run_install(
        "uv",
        "sync",
        "--extra",
        "types",
        "--frozen",
        "--python",
        PY_LATEST,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    command = ["python", "-m", "mypy", "."]
    if session.posargs and all(arg for arg in session.posargs):
        command.append(*session.posargs)
    session.run(*command)


@nox.session
def lint(session):
    session.run(
        "uv",
        "run",
        "--with",
        "pre-commit-uv",
        "--python",
        PY_LATEST,
        "pre-commit",
        "run",
        "--all-files",
    )


@nox.session
def gha_matrix(session):
    sessions = session.run("nox", "-l", "--json", silent=True)
    matrix = {
        "include": [
            {
                "python-version": session["python"],
                "django-version": session["call_spec"]["django"],
            }
            for session in json.loads(sessions)
            if session["name"] == "tests"
        ]
    }
    with Path(os.environ["GITHUB_OUTPUT"]).open("a") as fh:
        print(f"matrix={matrix}", file=fh)


@nox.session
def benchmark(session):
    session.run_install("maturin", "develop", "--uv")
    session.run_install(
        "uv",
        "sync",
        "--locked",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    session.run("python", "benchmark.py")
