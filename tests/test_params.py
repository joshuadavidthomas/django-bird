from __future__ import annotations

import pytest

from django_bird.components import Component
from django_bird.params import Param
from django_bird.params import Params
from django_bird.params import Value
from django_bird.templatetags.tags.bird import BirdNode

from .utils import TestComponent


class TestValue:
    @pytest.mark.parametrize(
        "value,context,expected",
        [
            (Value('"btn"'), {"btn": "blue"}, "btn"),
            (Value("btn"), {"btn": "blue"}, "blue"),
            (Value(True), {}, True),
            (Value(None), {}, None),
            (Value("True"), {}, True),
            (Value("False"), {}, None),
            (Value("undefined"), {}, "undefined"),
            (Value("foo.bar"), {}, "foo.bar"),
            (Value("foo.bar"), {"foo": {}}, "foo.bar"),
        ],
    )
    def test_resolve(self, value, context, expected):
        assert value.resolve(context) == expected


class TestParam:
    @pytest.mark.parametrize(
        "param,context,expected",
        [
            (Param(name="class", value=Value("btn")), {}, 'class="btn"'),
            (
                Param(name="class", value=Value("btn")),
                {"btn": "blue"},
                'class="blue"',
            ),
            (Param(name="disabled", value=Value(True)), {}, "disabled"),
            (Param(name="disabled", value=Value(None)), {}, ""),
            (
                Param(name="class", value=Value('"btn"')),
                {"btn": "blue"},
                'class="btn"',
            ),
            (
                Param(name="class", value=Value("'item.name'")),
                {"item": {"name": "value"}},
                'class="item.name"',
            ),
            (
                Param(name="class", value=Value("undefined")),
                {},
                'class="undefined"',
            ),
            (
                Param(name="class", value=Value("foo.bar")),
                {},
                'class="foo.bar"',
            ),
            (
                Param(name="class", value=Value("foo.bar")),
                {"foo": {}},
                'class="foo.bar"',
            ),
            (Param(name="hx_get", value=Value("/")), {}, 'hx-get="/"'),
        ],
    )
    def test_render_attr(self, param, context, expected):
        assert param.render_attr(context) == expected

    @pytest.mark.parametrize(
        "param,context,expected",
        [
            (Param(name="class", value=Value("btn")), {}, "btn"),
            (
                Param(name="class", value=Value("btn")),
                {"btn": "blue"},
                "blue",
            ),
            (Param(name="disabled", value=Value(True)), {}, True),
            (Param(name="disabled", value=Value(None)), {}, None),
            (
                Param(name="count", value=Value("items.length")),
                {"items": {"length": 5}},
                5,
            ),
            (Param(name="isActive", value=Value("False")), {}, None),
            (Param(name="isActive", value=Value("True")), {}, True),
            (
                Param(name="data", value=Value("user.name")),
                {"user": {"name": "Alice"}},
                "Alice",
            ),
            (
                Param(name="data", value=Value("'user.name'")),
                {"user": {"name": "Alice"}},
                "user.name",
            ),
            (
                Param(name="class", value=Value("undefined")),
                {},
                "undefined",
            ),
            (
                Param(name="data", value=Value("user.name")),
                {},
                "user.name",
            ),
            (
                Param(name="data", value=Value("user.name")),
                {"user": {}},
                "user.name",
            ),
        ],
    )
    def test_render_prop(self, param, context, expected):
        assert param.render_prop(context) == expected

    @pytest.mark.parametrize(
        "bit,expected",
        [
            ("class='btn'", Param(name="class", value=Value("'btn'"))),
            ('class="btn"', Param(name="class", value=Value('"btn"'))),
            ("class=btn", Param(name="class", value=Value("btn"))),
            ("disabled", Param(name="disabled", value=Value(True))),
            (
                "class=item.name",
                Param(name="class", value=Value("item.name")),
            ),
            (
                'class="item.name"',
                Param(name="class", value=Value('"item.name"')),
            ),
        ],
    )
    def test_from_bit(self, bit, expected):
        assert Param.from_bit(bit) == expected


class TestParams:
    @pytest.mark.parametrize(
        "params,test_component,context,expected_props,expected_attrs",
        [
            (
                Params(attrs=[Param(name="class", value=Value(None))]),
                TestComponent(name="test", content="{% bird:prop class='btn' %}"),
                {},
                {"class": "btn"},
                [],
            ),
            (
                Params(attrs=[Param(name="class", value=Value("btn"))]),
                TestComponent(name="test", content="{% bird:prop class %}"),
                {},
                {"class": "btn"},
                [],
            ),
            (
                Params(attrs=[Param(name="class", value=Value("btn"))]),
                TestComponent(name="test", content=""),
                {},
                {},
                [Param(name="class", value=Value("btn"))],
            ),
            (
                Params(attrs=[Param(name="class", value=Value("'static'"))]),
                TestComponent(name="test", content="{% bird:prop class %}"),
                {"static": "dynamic"},
                {"class": "static"},
                [],
            ),
            (
                Params(attrs=[Param(name="class", value=Value("var"))]),
                TestComponent(name="test", content="{% bird:prop class %}"),
                {"var": "dynamic"},
                {"class": "dynamic"},
                [],
            ),
            (
                Params(attrs=[Param(name="class", value=Value("undefined"))]),
                TestComponent(name="test", content="{% bird:prop class %}"),
                {},
                {"class": "undefined"},
                [],
            ),
            (
                Params(attrs=[Param(name="class", value=Value("user.name"))]),
                TestComponent(name="test", content="{% bird:prop class %}"),
                {},
                {"class": "user.name"},
                [],
            ),
        ],
    )
    def test_render_props(
        self,
        params,
        test_component,
        context,
        expected_props,
        expected_attrs,
        templates_dir,
    ):
        test_component.create(templates_dir)
        component = Component.from_name(test_component.name)
        assert params.render_props(component, context) == expected_props
        assert params.attrs == expected_attrs

    @pytest.mark.parametrize(
        "params,context,expected",
        [
            (
                Params(attrs=[Param(name="class", value=Value("btn"))]),
                {},
                'class="btn"',
            ),
            (
                Params(attrs=[Param(name="class", value=Value("btn"))]),
                {"btn": "blue"},
                'class="blue"',
            ),
            (Params(attrs=[Param(name="disabled", value=Value(True))]), {}, "disabled"),
            (
                Params(
                    attrs=[
                        Param(name="class", value=Value("btn")),
                        Param(name="disabled", value=Value(True)),
                    ]
                ),
                {},
                'class="btn" disabled',
            ),
            (
                Params(attrs=[Param(name="class", value=Value("'static'"))]),
                {"static": "dynamic"},
                'class="static"',
            ),
            (
                Params(attrs=[Param(name="class", value=Value("var"))]),
                {"var": "dynamic"},
                'class="dynamic"',
            ),
            (
                Params(attrs=[Param(name="class", value=Value("undefined"))]),
                {},
                'class="undefined"',
            ),
            (
                Params(attrs=[Param(name="class", value=Value("user.name"))]),
                {},
                'class="user.name"',
            ),
            (
                Params(attrs=[Param(name="class", value=Value("user.name"))]),
                {"user": {}},
                'class="user.name"',
            ),
        ],
    )
    def test_render_attrs(self, params, context, expected):
        assert params.render_attrs(context) == expected

    @pytest.mark.parametrize(
        "attrs,expected",
        [
            (
                ['class="btn"'],
                Params(attrs=[Param(name="class", value=Value('"btn"'))]),
            ),
            (
                ['class="btn"', 'id="my-btn"'],
                Params(
                    attrs=[
                        Param(name="class", value=Value('"btn"')),
                        Param(name="id", value=Value('"my-btn"')),
                    ]
                ),
            ),
            (
                ["disabled"],
                Params(attrs=[Param(name="disabled", value=Value(True))]),
            ),
            (
                ["class=dynamic"],
                Params(attrs=[Param(name="class", value=Value("dynamic"))]),
            ),
            (
                ["class=item.name", "id=user.id"],
                Params(
                    attrs=[
                        Param(name="class", value=Value("item.name")),
                        Param(name="id", value=Value("user.id")),
                    ]
                ),
            ),
        ],
    )
    def test_from_node(self, attrs, expected):
        node = BirdNode(name="test", attrs=attrs, nodelist=None)
        assert Params.from_node(node) == expected
