from __future__ import annotations

import importlib

import pluggy

import django_bird
from django_bird.plugins import hookspecs

DEFAULT_PLUGINS: list[str] = []

pm = pluggy.PluginManager(django_bird.__name__)
pm.add_hookspecs(hookspecs)

for plugin in DEFAULT_PLUGINS:
    mod = importlib.import_module(plugin)
    pm.register(mod, plugin)
