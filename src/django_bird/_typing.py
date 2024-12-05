from __future__ import annotations

import sys
from typing import TypeGuard

from django.template.base import Node
from django.template.base import Template

if sys.version_info >= (3, 12):
    from typing import override as typing_override
else:
    from typing_extensions import (
        override as typing_override,  # pyright: ignore[reportUnreachable]
    )

override = typing_override

TagBits = list[str]


def _has_nodelist(node: Template | Node) -> TypeGuard[Template]:
    return hasattr(node, "nodelist")
