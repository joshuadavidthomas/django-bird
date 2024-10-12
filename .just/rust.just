set unstable := true

justfile := justfile_directory() + "/.just/rust.just"

[private]
default:
    @just --list --justfile {{ justfile }}

[private]
fmt:
    @just --fmt --justfile {{ justfile }}

set working-directory := "../src/_bird_loader"

cargo *ARGS:
    cargo {{ ARGS }}
