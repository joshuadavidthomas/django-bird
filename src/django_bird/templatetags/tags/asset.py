# pyright: reportAny=false
from __future__ import annotations

from enum import Enum
from typing import final

from django import template
from django.template.base import Parser
from django.template.base import Token
from django.template.context import Context

from django_bird._typing import override


class AssetTag(Enum):
    CSS = "bird:css"
    JS = "bird:js"


def do_asset(_parser: Parser, token: Token) -> AssetNode:
    bits = token.split_contents()
    if len(bits) < 1:
        msg = "bird:assets tag requires at least one argument"
        raise template.TemplateSyntaxError(msg)
    tag_name = bits[0]
    asset_tag = AssetTag(tag_name)
    return AssetNode(asset_tag)


@final
class AssetNode(template.Node):
    def __init__(self, asset_tag: AssetTag):
        self.asset_tag = asset_tag

    @override
    def render(self, context: Context) -> str:
        from django_bird.components import components

        template = getattr(context, "template", None)
        if not template:
            return ""
        used_components = components.get_component_usage(template.origin.name)
        assets = set(
            asset
            for component in used_components
            for asset in component.assets
            if asset.type.tag == self.asset_tag
        )
        if not assets:
            return ""
        rendered = [asset.render() for asset in sorted(assets, key=lambda a: a.path)]
        return "\n".join(rendered)
