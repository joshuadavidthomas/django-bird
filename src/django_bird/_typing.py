from __future__ import annotations

import sys

from django.template.base import FilterExpression

if sys.version_info >= (3, 12):
    from typing import override as typing_override
else:
    from typing_extensions import override as typing_override

override = typing_override

RawTagBits = list[str]
ParsedTagBits = dict[str, FilterExpression]
