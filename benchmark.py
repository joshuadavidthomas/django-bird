from __future__ import annotations

import timeit

from django_bird.compiler import Compiler


def benchmark_compilation(template_string):
    compiler = Compiler()

    def compile_template():
        compiler.compile(template_string)

    number = 1000  # number of times to run the test
    time_taken = timeit.timeit(compile_template, number=number)
    print(f"Average time to compile: {time_taken/number:.6f} seconds")


small_template = "<bird:div>Hello, World!</bird:div>"
medium_template = (
    "<bird:div><bird:p>Paragraph 1</bird:p><bird:p>Paragraph 2</bird:p></bird:div>"
)
large_template = "<bird:div>" + "<bird:p>Paragraph</bird:p>" * 1000 + "</bird:div>"

benchmark_compilation(small_template)
benchmark_compilation(medium_template)
benchmark_compilation(large_template)
