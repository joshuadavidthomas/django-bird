set unstable := true

justfile := justfile_directory() + "/.just/project.just"

[private]
default:
    @just --list --justfile {{ justfile }}

[private]
fmt:
    @just --fmt --justfile {{ justfile }}

[no-cd]
@bump *ARGS:
    {{ justfile_directory() }}/.bin/bump.py version {{ ARGS }}

[no-cd]
@release *ARGS:
    {{ justfile_directory() }}/.bin/bump.py release {{ ARGS }}
