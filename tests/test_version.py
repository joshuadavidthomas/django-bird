from __future__ import annotations

from django_bird import __version__


def test_version():
    assert __version__ == "0.1.0a0"