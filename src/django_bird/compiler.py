from __future__ import annotations

import re

BIRD_PATTERN = re.compile(
    r"<bird:(\w+)([^>]*)(?:/>|>(.*?)</bird:\1>)", re.DOTALL | re.MULTILINE
)


class Compiler:
    # placeholder for now, implementation to come
    def compile(self, input_string: str) -> str:
        tokens = self.tokenize(input_string)
        ast = self.parse(tokens)
        return self.transform(ast)

    def tokenize(self, input_string: str) -> str:
        return input_string

    def parse(self, tokens: str) -> str:
        return tokens

    def transform(self, ast: str) -> str:
        return ast
