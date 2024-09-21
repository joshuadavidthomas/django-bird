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
<!-- [[[end]]] -->
