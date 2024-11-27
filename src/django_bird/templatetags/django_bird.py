# pyright: reportAny=false
from __future__ import annotations

from django import template

from .tags import do_bird
from .tags import do_slot

register = template.Library()


register.tag("bird", do_bird)
register.tag("bird:slot", do_slot)
