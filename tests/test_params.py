from __future__ import annotations

import pytest

from django_bird.params import Param
from django_bird.params import Params
from django_bird.params import Value
from django_bird.templatetags.tags.prop import PropNode


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
        "params,nodelist,context,expected_props,expected_attrs",
        [
            (
                Params(attrs=[Param(name="class", value=Value(None))]),
                [PropNode(name="class", default="btn", attrs=[])],
                {},
                {"class": "btn"},
                [],
            ),
            (
                Params(attrs=[Param(name="class", value=Value("btn", quoted=False))]),
                [PropNode(name="class", default=None, attrs=[])],
                {},
                {"class": "btn"},
                [],
            ),
            (
                Params(attrs=[Param(name="class", value=Value("btn", quoted=False))]),
                None,
                {},
                None,
                [Param(name="class", value=Value("btn", quoted=False))],
            ),
            (
                Params(attrs=[Param(name="class", value=Value("static", quoted=True))]),
                [PropNode(name="class", default=None, attrs=[])],
                {"static": "dynamic"},
                {"class": "static"},
                [],
            ),
            (
                Params(attrs=[Param(name="class", value=Value("var", quoted=False))]),
                [PropNode(name="class", default=None, attrs=[])],
                {"var": "dynamic"},
                {"class": "dynamic"},
                [],
            ),
            (
                Params(
                    attrs=[Param(name="class", value=Value("undefined", quoted=False))]
                ),
                [PropNode(name="class", default=None, attrs=[])],
                {},
                {"class": "undefined"},
                [],
            ),
            (
                Params(
                    attrs=[Param(name="class", value=Value("user.name", quoted=False))]
                ),
                [PropNode(name="class", default=None, attrs=[])],
                {},
                {"class": "user.name"},
                [],
            ),
        ],
    )
    def test_render_props(
        self, params, nodelist, context, expected_props, expected_attrs
    ):
        assert params.render_props(nodelist, context) == expected_props
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
