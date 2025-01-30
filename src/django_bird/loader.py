from __future__ import annotations

from django.template.base import Origin
from django.template.engine import Engine
from django.template.loaders.filesystem import Loader as FileSystemLoader

from ._typing import override


class BirdLoader(FileSystemLoader):
    def __init__(self, engine: Engine):
        super().__init__(engine)

    @override
    def get_contents(self, origin: Origin) -> str:
        return super().get_contents(origin)
