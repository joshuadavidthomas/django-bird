from __future__ import annotations

from django import template

from .tags import asset
from .tags import bird
from .tags import prop
from .tags import slot
from .tags import var

register = template.Library()


register.tag(asset.AssetTag.CSS.value, asset.do_asset)
register.tag(asset.AssetTag.JS.value, asset.do_asset)
register.tag(bird.TAG, bird.do_bird)
register.tag(prop.TAG, prop.do_prop)
register.tag(slot.TAG, slot.do_slot)
register.tag(var.TAG, var.do_var)
register.tag(var.END_TAG, var.do_end_var)
