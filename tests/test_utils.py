from __future__ import annotations

import pytest

from django_bird.utils import get_files_from_dirs
from django_bird.utils import unique_ordered


def test_get_files_from_dirs(tmp_path):
    first = tmp_path / "first"
    first.mkdir()

    for i in range(10):
        file = first / f"to_find{i}.txt"
        file.write_text("file should be found")

    for i in range(10):
        file = first / f"do_not_find{i}.txt"
        file.write_text("file should not be found")

    second = tmp_path / "second"
    second.mkdir()

    for i in range(10):
        file = second / f"to_find{i}.txt"
        file.write_text("file should be found")

    for i in range(10):
        file = second / f"do_not_find{i}.txt"
        file.write_text("file should not be found")

    dirs = [first, second]

    found_paths = list(get_files_from_dirs(dirs, "to_find*.txt"))

    assert len(found_paths) == 20
    assert all("to_find" in path.name for path, _ in found_paths)
    assert not any("do_not_find" in path.name for path, _ in found_paths)


@pytest.mark.parametrize(
    "items,expected",
    [
        (["a", "b", "c", "a"], ["a", "b", "c"]),
        (["first", "second", "first", "third"], ["first", "second", "third"]),
        ([1, 2, 1, 3], [1, 2, 3]),
        ([1, "b", 1, "a"], [1, "b", "a"]),
    ],
)
def test_unique_ordered(items, expected):
    assert unique_ordered(items) == expected
