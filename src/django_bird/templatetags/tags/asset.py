# pyright: reportAny=false
from __future__ import annotations

from django import template
from django.template.base import Parser
from django.template.base import Token
from django.template.context import Context

from django_bird._typing import TagBits
from django_bird._typing import override
from django_bird.staticfiles import AssetType

CSS_TAG = "bird:css"
JS_TAG = "bird:js"


def do_asset(parser: Parser, token: Token) -> AssetNode:
    bits = token.split_contents()
    asset_type = parse_asset_type(bits)
    return AssetNode(asset_type)


def parse_asset_type(bits: TagBits) -> AssetType:
    tag_name = bits[0]

    if len(bits) < 1:
        msg = f"{tag_name} tag requires at least one argument"
        raise template.TemplateSyntaxError(msg)

    try:
        asset_type = tag_name.split(":")[1]
        match asset_type:
            case "css":
                return AssetType.CSS
            case "js":
                return AssetType.JS
            case _:
                raise ValueError(f"Unknown asset type: {asset_type}")
    except IndexError as e:
        raise ValueError(f"Invalid tag name: {tag_name}") from e


class AssetNode(template.Node):
    def __init__(self, asset_type: AssetType):
        self.asset_type = asset_type

    @override
    def render(self, context: Context) -> str:
        # TODO
        return ""
