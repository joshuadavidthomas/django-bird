from __future__ import annotations

from django_bird.compiler import Compiler


def test_compiler():
    component_template = """
<style>
    body { font-family: Arial, sans-serif; }
</style>

<h1>Welcome to my page</h1>
{{ user.name }}

<script>
    console.log('Hello, world!');
</script>

<p>This is some more content.</p>

<style>
    .highlight { color: red; }
</style>
"""
    compiler = Compiler()

    tokens = compiler.tokenize(component_template)
    ast = compiler.parse(tokens)
    transformed = compiler.transform(ast)
    compiled = compiler.compile(component_template)

    assert tokens
    assert ast
    assert transformed
    assert compiled
