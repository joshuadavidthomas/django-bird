# Contributing

All contributions are welcome! Besides code contributions, this includes things like documentation improvements, bug reports, and feature requests.

You should first check if there is a [GitHub issue](https://github.com/joshuadavidthomas/bird/issues) already open or related to what you would like to contribute. If there is, please comment on that issue to let others know you are working on it. If there is not, please open a new issue to discuss your contribution.

Not all contributions need to start with an issue, such as typo fixes in documentation or version bumps to Python or Django that require no internal code changes, but generally, it is a good idea to open an issue first.

We adhere to Django's Code of Conduct in all interactions and expect all contributors to do the same. Please read the [Code of Conduct](https://www.djangoproject.com/conduct/) before contributing.

## Setup

The following setup steps assume you are using a Unix-like operating system, such as Linux or macOS, and that you have a [supported](README.md#requirements) version of Python installed. If you are using Windows, you will need to adjust the commands accordingly. If you do not have Python installed, you can visit [python.org](https://www.python.org/) for instructions on how to install it for your operating system.

1. Fork the repository and clone it locally.
2. Create a virtual environment and activate it. You can use whatever tool you prefer for this. Below is an example using the Python standard library's `venv` module:

```shell
python -m venv venv
source venv/bin/activate
```

3. Install `bird` and the `dev` dependencies in editable mode:

```shell
python -m pip install --editable '.[dev]'
# or using [just](#just)
just bootstrap
```

## Testing

We use [`pytest`](https://docs.pytest.org/) for testing and [`nox`](https://nox.thea.codes/) to run the tests in multiple environments.

To run the test suite against the default versions of Python (lower bound of supported versions) and Django (lower bound of LTS versions), run:

```shell
python -m nox --session "test"
# or using [just](#just)
just test
```

To run the test suite against all supported versions of Python and Django, run:

```shell
python -m nox --session "tests"
# or using [just](#just)
just testall
```

## `just`

[`just`](https://github.com/casey/just) is a command runner that is used to run common commands, similar to `make` or `invoke`. A `Justfile` is provided at the base of the repository, which contains commands for common development tasks, such as running the test suite or linting.

To see a list of all available commands, ensure `just` is installed and run the following command at the base of the repository:

```shell
just
```
