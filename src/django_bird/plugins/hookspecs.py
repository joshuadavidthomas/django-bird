from __future__ import annotations

from pluggy import HookimplMarker
from pluggy import HookspecMarker

import django_bird

hookspec = HookspecMarker(django_bird.__name__)
hookimpl = HookimplMarker(django_bird.__name__)
