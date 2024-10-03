from __future__ import annotations

import cProfile
import pstats

from django_bird.compiler import Compiler


def compile_template(template):
    compiler = Compiler()
    return compiler.compile(template)


large_template = "<bird:div>" + "<bird:p>Paragraph</bird:p>" * 1000 + "</bird:div>"

cProfile.runctx(
    "compile_template(large_template)", globals(), locals(), "compiler_stats"
)

p = pstats.Stats("compiler_stats")
p.strip_dirs().sort_stats("cumulative").print_stats(20)
