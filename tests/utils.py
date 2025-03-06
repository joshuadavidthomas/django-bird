from __future__ import annotations

import re
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

from django_bird.staticfiles import AssetType


@dataclass
class TestComponent:
    __test__ = False

    name: str
    content: str
    file: Path | None = None
    parent_dir: str = "bird"
    sub_dir: str | None = None

    def create(self, base_dir: Path) -> TestComponent:
        parent = base_dir / self.parent_dir
        parent.mkdir(exist_ok=True)

        if self.sub_dir is not None:
            dir = parent / self.sub_dir
            dir.mkdir(exist_ok=True)
        else:
            dir = parent

        template = dir / f"{self.name}.html"
        template.write_text(self.content)

        self.file = template

        return self


@dataclass
class TestAsset:
    __test__ = False

    component: TestComponent
    content: str
    asset_type: AssetType
    file: Path | None = None

    def create(self) -> TestAsset:
        if self.component.file is None:
            raise ValueError("Component must be created before adding assets")

        component_dir = self.component.file.parent
        component_name = self.component.file.stem

        asset_file = component_dir / f"{component_name}.{self.asset_type.extension}"
        asset_file.write_text(self.content)

        self.file = asset_file

        return self

    @property
    def relative_file_path(self):
        component_dir = Path(self.component.parent_dir)
        if self.component.sub_dir:
            component_dir = component_dir / self.component.sub_dir
        return Path(component_dir / self.file.name)


@dataclass
class TestComponentCase:
    __test__ = False

    component: TestComponent
    template_content: str
    expected: str
    description: str = ""
    template_context: dict[str, Any] = field(default_factory=dict)


def print_directory_tree(root_dir: str | Path, prefix: str = ""):
    root_path = Path(root_dir)
    contents = sorted(root_path.iterdir())
    pointers = ["├── "] * (len(contents) - 1) + ["└── "]
    for pointer, path in zip(pointers, contents, strict=False):
        print(prefix + pointer + path.name)
        if path.is_dir():
            extension = "│   " if pointer == "├── " else "    "
            print_directory_tree(path, prefix=prefix + extension)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in rendered template output"""
    # multiple whitespace characters
    text = re.sub(r"\s+", " ", text)
    # after opening tag, including when there are attributes
    text = re.sub(r"<(\w+)(\s+[^>]*)?\s*>", r"<\1\2>", text)
    # before closing tag
    text = re.sub(r"\s+>", ">", text)
    # after opening tag and before closing tag
    text = re.sub(r">\s+<", "><", text)
    # immediately after opening tag (including attributes) or before closing tag
    text = re.sub(r"(<\w+(?:\s+[^>]*)?>)\s+|\s+(<\/\w+>)", r"\1\2", text)
    # between tags and text content
    text = re.sub(r">\s+([^<])", r">\1", text)
    text = re.sub(r"([^>])\s+<", r"\1<", text)
    return text.strip()
