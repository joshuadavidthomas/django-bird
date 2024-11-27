from __future__ import annotations

from django import template

from .tags import bird
from .tags import slot

register = template.Library()


register.tag(bird.TAG, bird.do_bird)
register.tag(slot.TAG, slot.do_slot)
