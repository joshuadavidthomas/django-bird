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
PY314 = "3.14"
PY_VERSIONS = [PY310, PY311, PY312, PY313, PY314]
PY_DEFAULT = PY_VERSIONS[0]
PY_LATEST = PY_VERSIONS[-1]

DJ52 = "5.2"
DJ60 = "6.0"
DJ61 = "6.1"
DJMAIN = "main"
DJ_VERSIONS = [DJ52, DJ60, DJ61, DJMAIN]
DJANGO_MIN_PYTHON = {
    DJ52: PY310,
    DJ60: PY312,
    DJ61: PY312,
    DJMAIN: PY312,
}
DJ_DEFAULT = DJ52


def version(ver: str) -> tuple[int, ...]:
    """Convert a string version to a tuple of ints, e.g. "3.10" -> (3, 10)"""
    return tuple(map(int, ver.split(".")))


def should_skip(python: str, django: str) -> bool:
    """Return True if the test should be skipped"""

    return version(python) < version(DJANGO_MIN_PYTHON[django])


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
    if session.posargs:
        args = []
        for arg in session.posargs:
            if arg:
                args.extend(arg.split(" "))
        command.extend(args)
    session.run(*command)


@nox.session
def coverage(session):
    session.run_install(
        "uv",
        "sync",
        "--frozen",
        "--python",
        PY_DEFAULT,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    try:
        command = ["python", "-m", "pytest", "--cov", "--cov-report="]
        if session.posargs:
            args = []
            for arg in session.posargs:
                if arg:
                    args.extend(arg.split(" "))
            command.extend(args)
        session.run(*command)
    finally:
        # 0 -> OK
        # 2 -> code coverage percent unmet
        success_codes = [0, 2]

        report_cmd = ["python", "-m", "coverage", "report", "--show-missing"]
        session.run(*report_cmd, success_codes=success_codes)

        if summary := os.getenv("GITHUB_STEP_SUMMARY"):
            report_cmd.extend(["--skip-covered", "--skip-empty", "--format=markdown"])

            with Path(summary).open("a") as output_buffer:
                output_buffer.write("")
                output_buffer.write("### Coverage\n\n")
                output_buffer.flush()
                session.run(
                    *report_cmd, stdout=output_buffer, success_codes=success_codes
                )
        else:
            session.run(
                "python",
                "-m",
                "coverage",
                "html",
                "--skip-covered",
                "--skip-empty",
                success_codes=success_codes,
            )


@nox.session
def mypy(session):
    session.run_install(
        "uv",
        "sync",
        "--group",
        "types",
        "--frozen",
        "--python",
        PY_LATEST,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    command = ["python", "-m", "mypy", "."]
    if session.posargs:
        args = []
        for arg in session.posargs:
            if arg:
                args.extend(arg.split(" "))
        command.extend(args)
    session.run(*command)


@nox.session
def pyright(session):
    session.run_install(
        "uv",
        "sync",
        "--group",
        "types",
        "--frozen",
        "--python",
        PY_LATEST,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    command = ["basedpyright"]
    if session.posargs:
        args = []
        for arg in session.posargs:
            if arg:
                args.extend(arg.split(" "))
        command.extend(args)
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
