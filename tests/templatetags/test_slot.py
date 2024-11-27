from __future__ import annotations

import pytest
from django.template import Context
from django.template import Template
from django.template.exceptions import TemplateSyntaxError

from django_bird.templatetags.tags.slot import parse_slot_name


@pytest.mark.parametrize(
    "bits,expected",
    [
        (["slot"], "default"),
        (["slot", "foo"], "foo"),
        (["slot", "'foo'"], "foo"),
        (["slot", '"foo"'], "foo"),
        (["slot", 'name="foo"'], "foo"),
        (["slot", "name='foo'"], "foo"),
    ],
)
def test_parse_slot_name(bits, expected):
    assert parse_slot_name(bits) == expected


def test_parse_slot_name_no_args():
    with pytest.raises(TemplateSyntaxError):
        assert parse_slot_name([])


class TestTemplateTag:
    @pytest.mark.parametrize(
        "template,context,expected",
        [
            ("{{ slot }}", {"slot": "test"}, "test"),
            ("{% bird:slot %}{% endbird:slot %}", {"slot": "test"}, "test"),
            ("{% bird:slot default %}{% endbird:slot %}", {"slot": "test"}, "test"),
            ("{% bird:slot 'default' %}{% endbird:slot %}", {"slot": "test"}, "test"),
            ('{% bird:slot "default" %}{% endbird:slot %}', {"slot": "test"}, "test"),
            (
                "{% bird:slot name='default' %}{% endbird:slot %}",
                {"slot": "test"},
                "test",
            ),
            (
                '{% bird:slot name="default" %}{% endbird:slot %}',
                {"slot": "test"},
                "test",
            ),
            (
                "{% bird:slot name='not-default' %}{% endbird:slot %}",
                {"slot": "test"},
                "",
            ),
            (
                "{% bird:slot outer %}Outer {% bird:slot inner %}Inner{% endbird:slot %} Content{% endbird:slot %}",
                {"slots": {"outer": "Replaced Content"}},
                "Replaced Content",
            ),
            (
                "{% bird:slot outer %}Outer {% bird:slot inner %}Inner{% endbird:slot %} Content{% endbird:slot %}",
                {"slots": {"inner": "Replaced Content"}},
                "Outer Replaced Content Content",
            ),
            (
                "{% bird:slot outer %}Outer {% bird:slot inner %}Inner Default{% endbird:slot %} Content{% endbird:slot %}",
                {
                    "slots": {
                        "outer": "Replaced {% bird:slot inner %}{% endbird:slot %} Outer",
                        "inner": "Replaced Inner",
                    },
                },
                "Replaced Replaced Inner Outer",
            ),
            (
                "{{ slot }}",
                {
                    "slot": "Replaced {% bird:slot inner %}{% endbird:slot %} Outer",
                    "slots": {
                        "inner": "Replaced Inner",
                    },
                },
                "Replaced Replaced Inner Outer",
            ),
            (
                "{% bird:slot %}{% endbird:slot %}",
                {},
                "",
            ),
            (
                "{% bird:slot %}Default content{% endbird:slot %}",
                {},
                "Default content",
            ),
            (
                "{% bird:slot 'mal formed' %}{% endbird:slot %}",
                {"slots": {"mal formed": "content"}},
                "content",
            ),
            (
                "{% bird:slot CaseSensitive %}{% endbird:slot %}",
                {"slots": {"CaseSensitive": "Upper", "casesensitive": "Lower"}},
                "Upper",
            ),
            (
                "{% bird:slot %}{% endbird:slot %}",
                {"slots": {"default": 42}},
                "42",
            ),
            (
                "{% bird:slot %}{% endbird:slot %}",
                {"slots": {"default": "<b>Bold</b>"}},
                "<b>Bold</b>",
            ),
            (
                "{% bird:slot unicode_slot %}{% endbird:slot %}",
                {"slots": {"unicode_slot": "こんにちは"}},
                "こんにちは",
            ),
        ],
    )
    def test_rendering(self, template, context, expected, create_bird_template):
        create_bird_template("test", template)
        t = Template(f"{{% bird test %}}{template}{{% endbird %}}")
        rendered = t.render(context=Context(context))
        assert rendered == expected

    def test_too_many_args(self):
        with pytest.raises(TemplateSyntaxError):
            Template("{% bird:slot too many args %}{% endbird:slot %}")
