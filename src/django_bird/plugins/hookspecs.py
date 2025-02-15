from __future__ import annotations

from pluggy import HookimplMarker
from pluggy import HookspecMarker

hookspec = HookspecMarker("django_bird")
hookimpl = HookimplMarker("django_bird")
