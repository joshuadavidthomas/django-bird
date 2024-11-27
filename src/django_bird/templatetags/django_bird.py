from __future__ import annotations

from django import template

from .tags import bird
from .tags import slot

register = template.Library()


register.tag(bird.BIRD_TAG, bird.do_bird)
register.tag(slot.SLOT_TAG, slot.do_slot)
