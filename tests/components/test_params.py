from __future__ import annotations

import pytest

from django_bird.components.params import Param
from django_bird.components.params import Params


class TestParam:
    @pytest.mark.parametrize(
        "param,context,expected",
        [
            (Param(name="class", value="btn"), {}, 'class="btn"'),
            (Param(name="class", value="btn"), {"btn": "blue"}, 'class="blue"'),
            (Param(name="disabled", value=True), {}, "disabled"),
            (Param(name="disabled", value=None), {}, ""),
        ],
    )
    def test_render(self, param, context, expected):
        assert param.render(context) == expected

    @pytest.mark.parametrize(
        "bit,expected",
        [
            ("class='btn'", Param(name="class", value="btn")),
            ('class="btn"', Param(name="class", value="btn")),
            ("disabled", Param(name="disabled", value=True)),
        ],
    )
    def test_from_bit(self, bit, expected):
        assert Param.from_bit(bit) == expected


class TestParams:
    @pytest.mark.parametrize(
        "params,context,expected",
        [
            (Params(attrs=[Param(name="class", value="btn")]), {}, 'class="btn"'),
            (
                Params(attrs=[Param(name="class", value="btn")]),
                {"btn": "blue"},
                'class="blue"',
            ),
            (Params(attrs=[Param(name="disabled", value=True)]), {}, "disabled"),
            (
                Params(
                    attrs=[
                        Param(name="class", value="btn"),
                        Param(name="disabled", value=True),
                    ]
                ),
                {},
                'class="btn" disabled',
            ),
        ],
    )
    def test_render_attrs(self, params, context, expected):
        assert params.render_attrs(context) == expected

    @pytest.mark.parametrize(
        "bits,expected",
        [
            (["class='btn'"], Params(attrs=[Param(name="class", value="btn")])),
            (['class="btn"'], Params(attrs=[Param(name="class", value="btn")])),
            (["disabled"], Params(attrs=[Param(name="disabled", value=True)])),
        ],
    )
    def test_from_bits(self, bits, expected):
        assert Params.from_bits(bits) == expected
