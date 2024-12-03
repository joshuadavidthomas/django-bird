from __future__ import annotations

from django import template

from .tags import asset
from .tags import bird
from .tags import prop
from .tags import slot

register = template.Library()


register.tag(asset.CSS_TAG, asset.do_asset)
register.tag(asset.JS_TAG, asset.do_asset)
register.tag(bird.TAG, bird.do_bird)
register.tag(prop.TAG, prop.do_prop)
register.tag(slot.TAG, slot.do_slot)
