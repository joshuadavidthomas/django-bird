from __future__ import annotations

from django import template

from .tags import bird
from .tags import slot

register = template.Library()


register.tag(bird.START_TAG, bird.do_bird)
register.tag(slot.START_TAG, slot.do_slot)
