from __future__ import annotations

import re
from typing import Match

from .components import transformer

BIRD_TAG_PATTERN = re.compile(r"<bird:(\w+)([^>]*)>(.*?)</bird:\1>")


class BirdCompiler:
    def __init__(self) -> None:
        self.transformer = transformer

    def compile(self, content: str) -> str:
        parts = content.splitlines()
        result = []

        for part in parts:
            if match := BIRD_TAG_PATTERN.search(part):
                transformed = [item for item in self.transform_bird_line(part, match)]
                result.append("".join(transformed))
            else:
                result.append(part)

        return "\n".join(result)

    def transform_bird_line(self, line: str, match: Match[str]):
        start, end = match.span()

        yield line[:start].strip()

        tag_name, attrs, content = match.groups()
        yield self.transformer.transform(tag_name, attrs, content)

        yield line[end:].strip()
