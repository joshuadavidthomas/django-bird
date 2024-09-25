from __future__ import annotations


class Compiler:
    def compile(self, input_string: str) -> str:
        tokens = self.tokenize(input_string)
        parsed = self.parse(tokens)
        return self.transform(parsed)

    def tokenize(self, input_string: str) -> str: ...

    def parse(self, tokens: str) -> str: ...

    def transform(self, parsed_content: str) -> str: ...
