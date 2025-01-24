from __future__ import annotations

import pytest

from django_bird.components import Component
from django_bird.params import Param
from django_bird.params import Params
from django_bird.params import Value

from .utils import TestComponent


class TestValue:
    @pytest.mark.parametrize(
        "value,context,expected",
        [
            (Value("btn", quoted=True), {"btn": "blue"}, "btn"),
            (Value("btn", quoted=False), {"btn": "blue"}, "blue"),
            (Value(True), {}, True),
            (Value(None), {}, None),
            (Value("True"), {}, True),
            (Value("False"), {}, None),
            (Value("undefined", quoted=False), {}, "undefined"),
            (Value("foo.bar", quoted=False), {}, "foo.bar"),
            (Value("foo.bar", quoted=False), {"foo": {}}, "foo.bar"),
        ],
    )
    def test_resolve(self, value, context, expected):
        assert value.resolve(context) == expected


class TestParam:
    @pytest.mark.parametrize(
        "param,context,expected",
        [
            (Param(name="class", value=Value("btn", quoted=False)), {}, 'class="btn"'),
            (
                Param(name="class", value=Value("btn", quoted=False)),
                {"btn": "blue"},
                'class="blue"',
            ),
            (Param(name="disabled", value=Value(True)), {}, "disabled"),
            (Param(name="disabled", value=Value(None)), {}, ""),
            (
                Param(name="class", value=Value("btn", quoted=True)),
                {"btn": "blue"},
                'class="btn"',
            ),
            (
                Param(name="class", value=Value("item.name", quoted=True)),
                {"item": {"name": "value"}},
                'class="item.name"',
            ),
            (
                Param(name="class", value=Value("undefined", quoted=False)),
                {},
                'class="undefined"',
            ),
            (
                Param(name="class", value=Value("foo.bar", quoted=False)),
                {},
                'class="foo.bar"',
            ),
            (
                Param(name="class", value=Value("foo.bar", quoted=False)),
                {"foo": {}},
                'class="foo.bar"',
            ),
            (Param(name="hx_get", value=Value("/", quoted=False)), {}, 'hx-get="/"'),
        ],
    )
    def test_render_attr(self, param, context, expected):
        assert param.render_attr(context) == expected

    @pytest.mark.parametrize(
        "param,context,expected",
        [
            (Param(name="class", value=Value("btn", quoted=False)), {}, "btn"),
            (
                Param(name="class", value=Value("btn", quoted=False)),
                {"btn": "blue"},
                "blue",
            ),
            (Param(name="disabled", value=Value(True)), {}, True),
            (Param(name="disabled", value=Value(None)), {}, None),
            (
                Param(name="count", value=Value("items.length", quoted=False)),
                {"items": {"length": 5}},
                5,
            ),
            (Param(name="isActive", value=Value("False")), {}, None),
            (Param(name="isActive", value=Value("True")), {}, True),
            (
                Param(name="data", value=Value("user.name", quoted=False)),
                {"user": {"name": "Alice"}},
                "Alice",
            ),
            (
                Param(name="data", value=Value("user.name", quoted=True)),
                {"user": {"name": "Alice"}},
                "user.name",
            ),
            (
                Param(name="class", value=Value("undefined", quoted=False)),
                {},
                "undefined",
            ),
            (
                Param(name="data", value=Value("user.name", quoted=False)),
                {},
                "user.name",
            ),
            (
                Param(name="data", value=Value("user.name", quoted=False)),
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
            ("class='btn'", Param(name="class", value=Value("btn", quoted=True))),
            ('class="btn"', Param(name="class", value=Value("btn", quoted=True))),
            ("class=btn", Param(name="class", value=Value("btn", quoted=False))),
            ("disabled", Param(name="disabled", value=Value(True))),
            (
                "class=item.name",
                Param(name="class", value=Value("item.name", quoted=False)),
            ),
            (
                'class="item.name"',
                Param(name="class", value=Value("item.name", quoted=True)),
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
                Params(attrs=[Param(name="class", value=Value("btn", quoted=False))]),
                TestComponent(name="test", content="{% bird:prop class %}"),
                {},
                {"class": "btn"},
                [],
            ),
            (
                Params(attrs=[Param(name="class", value=Value("btn", quoted=False))]),
                TestComponent(name="test", content=""),
                {},
                {},
                [Param(name="class", value=Value("btn", quoted=False))],
            ),
            (
                Params(attrs=[Param(name="class", value=Value("static", quoted=True))]),
                TestComponent(name="test", content="{% bird:prop class %}"),
                {"static": "dynamic"},
                {"class": "static"},
                [],
            ),
            (
                Params(attrs=[Param(name="class", value=Value("var", quoted=False))]),
                TestComponent(name="test", content="{% bird:prop class %}"),
                {"var": "dynamic"},
                {"class": "dynamic"},
                [],
            ),
            (
                Params(
                    attrs=[Param(name="class", value=Value("undefined", quoted=False))]
                ),
                TestComponent(name="test", content="{% bird:prop class %}"),
                {},
                {"class": "undefined"},
                [],
            ),
            (
                Params(
                    attrs=[Param(name="class", value=Value("user.name", quoted=False))]
                ),
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
                Params(attrs=[Param(name="class", value=Value("btn", quoted=False))]),
                {},
                'class="btn"',
            ),
            (
                Params(attrs=[Param(name="class", value=Value("btn", quoted=False))]),
                {"btn": "blue"},
                'class="blue"',
            ),
            (Params(attrs=[Param(name="disabled", value=Value(True))]), {}, "disabled"),
            (
                Params(
                    attrs=[
                        Param(name="class", value=Value("btn", quoted=False)),
                        Param(name="disabled", value=Value(True)),
                    ]
                ),
                {},
                'class="btn" disabled',
            ),
            (
                Params(attrs=[Param(name="class", value=Value("static", quoted=True))]),
                {"static": "dynamic"},
                'class="static"',
            ),
            (
                Params(attrs=[Param(name="class", value=Value("var", quoted=False))]),
                {"var": "dynamic"},
                'class="dynamic"',
            ),
            (
                Params(
                    attrs=[Param(name="class", value=Value("undefined", quoted=False))]
                ),
                {},
                'class="undefined"',
            ),
            (
                Params(
                    attrs=[Param(name="class", value=Value("user.name", quoted=False))]
                ),
                {},
                'class="user.name"',
            ),
            (
                Params(
                    attrs=[Param(name="class", value=Value("user.name", quoted=False))]
                ),
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
                [Param(name="class", value=Value("btn", quoted=True))],
                Params(attrs=[Param(name="class", value=Value("btn", quoted=True))]),
            ),
            (
                [
                    Param(name="class", value=Value("btn", quoted=True)),
                    Param(name="id", value=Value("my-btn", quoted=True)),
                ],
                Params(
                    attrs=[
                        Param(name="class", value=Value("btn", quoted=True)),
                        Param(name="id", value=Value("my-btn", quoted=True)),
                    ]
                ),
            ),
            (
                [Param(name="disabled", value=Value(True))],
                Params(attrs=[Param(name="disabled", value=Value(True))]),
            ),
            (
                [Param(name="class", value=Value("dynamic", quoted=False))],
                Params(
                    attrs=[Param(name="class", value=Value("dynamic", quoted=False))]
                ),
            ),
            (
                [
                    Param(name="class", value=Value("item.name", quoted=False)),
                    Param(name="id", value=Value("user.id", quoted=False)),
                ],
                Params(
                    attrs=[
                        Param(name="class", value=Value("item.name", quoted=False)),
                        Param(name="id", value=Value("user.id", quoted=False)),
                    ]
                ),
            ),
        ],
    )
    def test_with_attrs(self, attrs, expected):
        assert Params.with_attrs(attrs) == expected
