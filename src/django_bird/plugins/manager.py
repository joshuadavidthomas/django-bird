from __future__ import annotations

import importlib

import pluggy

from django_bird.plugins import hookspecs

pm = pluggy.PluginManager("django_bird")
pm.add_hookspecs(hookspecs)

DEFAULT_PLUGINS: list[str] = []

for plugin in DEFAULT_PLUGINS:
    mod = importlib.import_module(plugin)
    pm.register(mod, plugin)
