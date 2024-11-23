# Justfile

This project uses [Just](https://github.com/casey/just) as a command runner.

The following commands are available:

<!-- [[[cog
import subprocess
import cog

help = subprocess.run(['just', '--summary'], stdout=subprocess.PIPE)

for command in help.stdout.decode('utf-8').split(' '):
    command = command.strip()
    cog.outl(
        f"- [{command}](#{command})"
    )
]]] -->
- [bootstrap](#bootstrap)
- [coverage](#coverage)
- [lint](#lint)
- [lock](#lock)
- [manage](#manage)
- [test](#test)
- [testall](#testall)
- [types](#types)
- [copier::copy](#copier::copy)
- [copier::recopy](#copier::recopy)
- [copier::recopy-all](#copier::recopy-all)
- [copier::update](#copier::update)
- [copier::update-all](#copier::update-all)
- [docs::build](#docs::build)
- [docs::serve](#docs::serve)
- [project::bump](#project::bump)
- [project::release](#project::release)
<!-- [[[end]]] -->

## Commands

```{code-block} shell
:class: copy

$ just --list
```
<!-- [[[cog
import subprocess
import cog

list = subprocess.run(['just', '--list'], stdout=subprocess.PIPE)
cog.out(
    f"```\n{list.stdout.decode('utf-8')}\n```"
)
]]] -->
```
Available recipes:
    bootstrap
    coverage *ARGS
    lint
    lock *ARGS
    manage *COMMAND
    test *ARGS
    testall *ARGS
    types *ARGS
    copier ...
    docs ...
    project ...

```
<!-- [[[end]]] -->

<!-- [[[cog
import subprocess
import cog

summary = subprocess.run(['just', '--summary'], stdout=subprocess.PIPE)

for command in summary.stdout.decode('utf-8').split(' '):
    command = command.strip()
    cog.outl(
        f"### {command}\n"
    )
    cog.outl(
        f"```{{code-block}} shell\n"
        f":class: copy\n"
        f"\n$ just {command}\n"
        f"```\n"
    )
    command_show = subprocess.run(['just', '--show', command], stdout=subprocess.PIPE)
    cog.outl(
        f"```{{code-block}} shell\n{command_show.stdout.decode('utf-8')}```\n"
    )
]]] -->
### bootstrap

```{code-block} shell
:class: copy

$ just bootstrap
```

```{code-block} shell
bootstrap:
    uv python install
    uv sync --locked
```

### coverage

```{code-block} shell
:class: copy

$ just coverage
```

```{code-block} shell
coverage *ARGS:
    @just nox coverage {{ ARGS }}
```

### lint

```{code-block} shell
:class: copy

$ just lint
```

```{code-block} shell
lint:
    @just nox lint
```

### lock

```{code-block} shell
:class: copy

$ just lock
```

```{code-block} shell
lock *ARGS:
    uv lock {{ ARGS }}
```

### manage

```{code-block} shell
:class: copy

$ just manage
```

```{code-block} shell
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
```

### test

```{code-block} shell
:class: copy

$ just test
```

```{code-block} shell
test *ARGS:
    @just nox test {{ ARGS }}
```

### testall

```{code-block} shell
:class: copy

$ just testall
```

```{code-block} shell
testall *ARGS:
    @just nox tests {{ ARGS }}
```

### types

```{code-block} shell
:class: copy

$ just types
```

```{code-block} shell
types *ARGS:
    @just nox types {{ ARGS }}
```

### copier::copy

```{code-block} shell
:class: copy

$ just copier::copy
```

```{code-block} shell
# Create a copier answers file
[no-cd]
copy TEMPLATE_PATH DESTINATION_PATH=".":
    uv run copier copy --trust {{ TEMPLATE_PATH }} {{ DESTINATION_PATH }}
```

### copier::recopy

```{code-block} shell
:class: copy

$ just copier::recopy
```

```{code-block} shell
# Recopy the project from the original template
[no-cd]
recopy ANSWERS_FILE *ARGS:
    uv run copier recopy --trust --answers-file {{ ANSWERS_FILE }} {{ ARGS }}
```

### copier::recopy-all

```{code-block} shell
:class: copy

$ just copier::recopy-all
```

```{code-block} shell
# Loop through all answers files and recopy the project using copier
[no-cd]
@recopy-all *ARGS:
    for file in `ls .copier/`; do just copier recopy .copier/$file "{{ ARGS }}"; done
```

### copier::update

```{code-block} shell
:class: copy

$ just copier::update
```

```{code-block} shell
# Update the project using a copier answers file
[no-cd]
update ANSWERS_FILE *ARGS:
    uv run copier update --trust --answers-file {{ ANSWERS_FILE }} {{ ARGS }}
```

### copier::update-all

```{code-block} shell
:class: copy

$ just copier::update-all
```

```{code-block} shell
# Loop through all answers files and update the project using copier
[no-cd]
@update-all *ARGS:
    for file in `ls .copier/`; do just copier update .copier/$file "{{ ARGS }}"; done
```

### docs::build

```{code-block} shell
:class: copy

$ just docs::build
```

```{code-block} shell
# Build documentation using Sphinx
[no-cd]
build LOCATION="docs/_build/html": cog
    uv run --group docs sphinx-build docs {{ LOCATION }}
```

### docs::serve

```{code-block} shell
:class: copy

$ just docs::serve
```

```{code-block} shell
# Serve documentation locally
[no-cd]
serve PORT="8000": cog
    #!/usr/bin/env sh
    HOST="localhost"
    if [ -f "/.dockerenv" ]; then
        HOST="0.0.0.0"
    fi
    uv run --group docs sphinx-autobuild docs docs/_build/html --host "$HOST" --port {{ PORT }}
```

### project::bump

```{code-block} shell
:class: copy

$ just project::bump
```

```{code-block} shell
[no-cd]
@bump *ARGS:
    {{ justfile_directory() }}/.bin/bump.py version {{ ARGS }}
```

### project::release

```{code-block} shell
:class: copy

$ just project::release
```

```{code-block} shell
[no-cd]
@release *ARGS:
    {{ justfile_directory() }}/.bin/bump.py release {{ ARGS }}
```

<!-- [[[end]]] -->
