from __future__ import annotations

import cProfile
import os
import pstats
import timeit
from pathlib import Path

import pytest

from django_bird.compiler import Compiler

# Get the directory of this test file
TEST_DIR = Path(__file__).parent

# Define the templates
small_template = "<bird:div>Hello, World!</bird:div>"
medium_template = (
    "<bird:div><bird:p>Paragraph 1</bird:p><bird:p>Paragraph 2</bird:p></bird:div>"
)
large_template = "<bird:div>" + "<bird:p>Paragraph</bird:p>" * 1000 + "</bird:div>"


def compile_template(template):
    compiler = Compiler()
    return compiler.compile(template)


@pytest.mark.parametrize(
    "template, name",
    [(small_template, "small"), (medium_template, "medium"), (large_template, "large")],
)
def test_benchmark_compilation(template, name):
    compiler = Compiler()

    def compile_template():
        compiler.compile(template)

    number = 1000  # number of times to run the test
    time_taken = timeit.timeit(compile_template, number=number)
    avg_time = time_taken / number

    # Save results
    result_file = TEST_DIR / f"benchmark_{name}.txt"
    with open(result_file, "w") as f:
        f.write(f"Average time to compile {name} template: {avg_time:.6f} seconds")

    print(f"Average time to compile {name} template: {avg_time:.6f} seconds")
    assert True  # This test is for benchmarking, not for checking correctness


def test_profile_compilation():
    profile_file = TEST_DIR / "compiler_stats"
    cProfile.runctx(
        "compile_template(large_template)", globals(), locals(), str(profile_file)
    )

    # Create a stats object and print the results
    p = pstats.Stats(str(profile_file))
    stats_file = TEST_DIR / "profile_stats.txt"
    with open(stats_file, "w") as f:
        p.stream = f  # Redirect output to file
        p.strip_dirs().sort_stats("cumulative").print_stats(20)

    assert os.path.exists(stats_file)  # Check that the stats file was created
