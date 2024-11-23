#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "bumpver",
#     "typer",
# ]
# ///
from __future__ import annotations

import re
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import Annotated
from typing import Any

import typer
from typer import Option


class CommandRunner:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def _quote_arg(self, arg: str) -> str:
        if " " in arg and not (arg.startswith('"') or arg.startswith("'")):
            return f"'{arg}'"
        return arg

    def _build_command_args(self, **params: Any) -> str:
        args = []
        for key, value in params.items():
            key = key.replace("_", "-")
            if isinstance(value, bool) and value:
                args.append(f"--{key}")
            elif value is not None:
                args.extend([f"--{key}", self._quote_arg(str(value))])
        return " ".join(args)

    def run(
        self, cmd: str, name: str, *args: str, force_run: bool = False, **params: Any
    ) -> str:
        command_parts = [cmd, name]
        command_parts.extend(self._quote_arg(arg) for arg in args)
        if params:
            command_parts.append(self._build_command_args(**params))
        command = " ".join(command_parts)
        print(
            f"would run command: {command}"
            if self.dry_run and not force_run
            else f"running command: {command}"
        )

        if self.dry_run and not force_run:
            return ""

        success, output = self._run_command(command)
        if not success:
            print(f"{cmd} failed: {output}", file=sys.stderr)
            raise typer.Exit(1)
        return output

    def _run_command(self, command: str) -> tuple[bool, str]:
        try:
            output = subprocess.check_output(
                command, shell=True, text=True, stderr=subprocess.STDOUT
            ).strip()
            return True, output
        except subprocess.CalledProcessError as e:
            return False, e.output


_runner: CommandRunner | None = None


def run(cmd: str, name: str, *args: str, **params: Any) -> str:
    if _runner is None:
        raise RuntimeError("CommandRunner not initialized. Call init_runner first.")
    return _runner.run(cmd, name, *args, **params)


def init_runner(dry_run: bool = False) -> None:
    global _runner
    _runner = CommandRunner(dry_run)


def get_current_version():
    tags = run("git", "tag", "--sort=-creatordate", force_run=True).splitlines()
    return tags[0] if tags else ""


def get_new_version(version: Version, tag: Tag | None = None) -> str:
    output = run(
        "bumpver", "update", dry=True, tag=tag, force_run=True, **{version: True}
    )
    if match := re.search(r"New Version: (.+)", output):
        return match.group(1)
    return typer.prompt("Failed to get new version. Enter manually")


def get_release_version() -> str:
    log = run(
        "git",
        "log",
        "-1",
        "--pretty=format:%s",
        force_run=True,
    )
    if match := re.search(r"bump version .* -> ([\d.]+)", log):
        return match.group(1)
    print("Could not find version in latest commit message")
    raise typer.Exit(1)


def update_changelog(new_version: str) -> None:
    repo_url = run("git", "remote", "get-url", "origin").strip().replace(".git", "")
    changelog = Path("CHANGELOG.md")
    content = changelog.read_text()

    content = re.sub(
        r"## \[Unreleased\]",
        f"## [{new_version}]",
        content,
        count=1,
    )
    content = re.sub(
        rf"## \[{new_version}\]",
        f"## [Unreleased]\n\n## [{new_version}]",
        content,
        count=1,
    )
    content += f"[{new_version}]: {repo_url}/releases/tag/v{new_version}\n"
    content = re.sub(
        r"\[unreleased\]: .*\n",
        f"[unreleased]: {repo_url}/compare/v{new_version}...HEAD\n",
        content,
        count=1,
    )

    changelog.write_text(content)
    run("git", "add", ".")
    run("git", "commit", "-m", f"update CHANGELOG for version {new_version}")


def update_uv_lock(new_version: str) -> None:
    run("uv", "lock")

    changes = run("git", "status", "--porcelain", force_run=True)
    if "uv.lock" not in changes:
        print("No changes to uv.lock, skipping commit")
        return

    run("git", "add", "uv.lock")
    run("git", "commit", "-m", f"update uv.lock for version {new_version}")


cli = typer.Typer()


class Version(str, Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


class Tag(str, Enum):
    DEV = "dev"
    ALPHA = "alpha"
    BETA = "beta"
    RC = "rc"
    FINAL = "final"


@cli.command()
def version(
    version: Annotated[
        Version, Option("--version", "-v", help="The tag to add to the new version")
    ],
    tag: Annotated[Tag, Option("--tag", "-t", help="The tag to add to the new version")]
    | None = None,
    dry_run: Annotated[
        bool, Option("--dry-run", "-d", help="Show commands without executing")
    ] = False,
):
    init_runner(dry_run)

    current_version = get_current_version()
    changes = run(
        "git",
        "log",
        f"{current_version}..HEAD",
        "--pretty=format:- `%h`: %s",
        "--reverse",
        force_run=True,
    )

    new_version = get_new_version(version, tag)
    release_branch = f"release-v{new_version}"

    try:
        run("git", "checkout", "-b", release_branch)
    except Exception:
        run("git", "checkout", release_branch)

    run("bumpver", "update", tag=tag, **{version: True})

    title = run("git", "log", "-1", "--pretty=%s")

    update_changelog(new_version)
    update_uv_lock(new_version)

    run("git", "push", "--set-upstream", "origin", release_branch)
    run(
        "gh",
        "pr",
        "create",
        "--base",
        "main",
        "--head",
        release_branch,
        "--title",
        title,
        "--body",
        changes,
    )


@cli.command()
def release(
    dry_run: Annotated[
        bool, Option("--dry-run", "-d", help="Show commands without executing")
    ] = False,
    force: Annotated[bool, Option("--force", "-f", help="Skip safety checks")] = False,
):
    init_runner(dry_run)

    current_branch = run("git", "branch", "--show-current", force_run=True).strip()
    if current_branch != "main" and not force:
        print(
            f"Must be on main branch to create release (currently on {current_branch})"
        )
        raise typer.Exit(1)

    if run("git", "status", "--porcelain") and not force:
        print("Working directory is not clean. Commit or stash changes first.")
        raise typer.Exit(1)

    run("git", "fetch", "origin", "main")
    local_sha = run("git", "rev-parse", "@").strip()
    remote_sha = run("git", "rev-parse", "@{u}").strip()
    if local_sha != remote_sha and not force:
        print("Local main is not up to date with remote. Pull changes first.")
        raise typer.Exit(1)

    version = get_release_version()

    try:
        run("gh", "release", "view", f"v{version}")
        if not force:
            print(f"Release v{version} already exists!")
            raise typer.Exit(1)
    except Exception:
        pass

    if not force and not dry_run:
        typer.confirm(f"Create release v{version}?", abort=True)

    run("gh", "release", "create", f"v{version}", "--generate-notes")


if __name__ == "__main__":
    cli()
