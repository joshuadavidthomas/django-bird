from __future__ import annotations

import re
from typing import Any
from typing import final

from django import template
from django.template.base import Parser
from django.template.base import Token
from django.template.context import Context

from django_bird._typing import override

register = template.Library()

TAG = "bird:var"
END_TAG = "endbird:var"

OPERATOR_PATTERN = re.compile(r"(\w+)\s*(\+=|=)\s*(.+)")


def do_var(parser: Parser, token: Token):
    _tag, *bits = token.split_contents()
    if not bits:
        msg = f"'{TAG}' tag requires an assignment"
        raise template.TemplateSyntaxError(msg)

    var_assignment = bits.pop(0)
    match = re.match(OPERATOR_PATTERN, var_assignment)
    if not match:
        msg = (
            f"Invalid assignment in '{TAG}' tag: {var_assignment}. "
            f"Expected format: {TAG} variable='value' or {TAG} variable+='value'."
        )
        raise template.TemplateSyntaxError(msg)

    var_name, operator, var_value = match.groups()
    var_value = var_value.strip()
    value = parser.compile_filter(var_value)

    return VarNode(var_name, operator, value)


def do_end_var(_parser: Parser, token: Token):
    _tag, *bits = token.split_contents()
    if not bits:
        msg = f"{token.contents.split()[0]} tag requires a variable name"
        raise template.TemplateSyntaxError(msg)

    var_name = bits.pop(0)

    return EndVarNode(var_name)


@final
class VarNode(template.Node):
    def __init__(self, name: str, operator: str, value: Any):
        self.name = name
        self.operator = operator
        self.value = value

    @override
    def render(self, context: Context) -> str:
        if "vars" not in context:
            context["vars"] = {}

        value = self.value.resolve(context)

        if self.operator == "+=":
            previous = context["vars"].get(self.name, "")
            value = f"{previous}{value}"

        context["vars"][self.name] = value
        return ""


@final
class EndVarNode(template.Node):
    def __init__(self, name: str):
        self.name = name

    @override
    def render(self, context: Context) -> str:
        if "vars" in context and self.name in context["vars"]:
            del context["vars"][self.name]
        return ""
