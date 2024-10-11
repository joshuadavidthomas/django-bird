from __future__ import annotations

from django.template.base import Origin
from django.template.exceptions import TemplateDoesNotExist
from django.template.loaders.filesystem import Loader as FileSystemLoader

from _bird_loader import get_contents

from ._typing import override


class BirdLoader(FileSystemLoader):
    @override
    def get_contents(self, origin: Origin) -> str:
        try:
            contents = get_contents(origin.name, self.engine.file_charset)
            return contents
        except FileNotFoundError as err:
            raise TemplateDoesNotExist(origin) from err
