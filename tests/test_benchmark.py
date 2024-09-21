from __future__ import annotations

import statistics
import timeit

import pytest
from django.template.loader import get_template
from scipy import stats


def render_template(template, context):
    return template.render(context)


def benchmark_template(template_name, context, number=1000, repeat=5):
    template = get_template(template_name)
    return timeit.repeat(
        lambda: render_template(template, context), number=number, repeat=repeat
    )


def get_benchmark_stats(times):
    mean = statistics.mean(times)
    median = statistics.median(times)
    stdev = statistics.stdev(times) if len(times) > 1 else 0

    return {
        "mean": mean,
        "median": median,
        "stdev": stdev,
        "min": min(times),
        "max": max(times),
    }


def print_stats(name, stats):
    print(f"{name}:")
    print(f"  Mean: {stats['mean']:.4f} seconds")
    print(f"  Median: {stats['median']:.4f} seconds")
    print(f"  Std Dev: {stats['stdev']:.4f} seconds")
    print(f"  Min: {stats['min']:4f} seconds")
    print(f"  Max: {stats['max']:.4f} seconds")


@pytest.mark.parametrize(
    "count,perf_threshold",
    [
        (10, 1.05),
        (100, 1.05),
        (500, 1.05),
    ],
)
def test_bird_performance(count, perf_threshold):
    context = {"title": "Test Title", "content": "Test Content", "count": range(count)}

    without_bird_times = benchmark_template("without_bird.html", context)
    with_bird_times = benchmark_template("with_bird.html", context)

    without_bird_stats = get_benchmark_stats(without_bird_times)
    with_bird_stats = get_benchmark_stats(with_bird_times)

    print_stats("Template without <bird:> tag", without_bird_stats)
    print_stats("Template with <bird:> tag", with_bird_stats)

    without_bird_mean = without_bird_stats["mean"]
    with_bird_mean = with_bird_stats["mean"]

    difference = with_bird_mean - without_bird_mean
    percentage_increase = ((with_bird_mean / without_bird_mean) - 1) * 100

    print(f"\nMean Difference: {difference:.4f} seconds")
    print(f"Mean Percentage increase: {percentage_increase:.2f}%")

    t_statistic, p_value = stats.ttest_ind(without_bird_times, with_bird_times)

    print(f"\nt-statistic: {t_statistic}")
    print(f"p-value: {p_value}")

    assert (
        with_bird_mean < without_bird_mean * perf_threshold
    ), f"Bird compilation shouldn't take more than {(perf_threshold - 1) * 100:.0f}% longer on average"
    assert p_value > 0.05, "The difference in performance is statistically significant"


def test_output_correctness():
    context = {"title": "Test Title", "content": "Test Content", "count": range(1)}

    without_bird_template = get_template("without_bird.html")
    with_bird_template = get_template("with_bird.html")

    without_bird_output = render_template(without_bird_template, context)
    with_bird_output = render_template(with_bird_template, context)

    expected_output = """
<div><h1>Test Title</h1><p>Test Content</p><button class="btn btn-primary">Click me</button></div>
""".strip()

    assert without_bird_output.strip() == expected_output
    assert with_bird_output.strip() == expected_output
