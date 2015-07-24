from os import path
import datetime

from django import template
from django.template.base import add_to_builtins
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

import ttag
from ttag.tests.setup import as_tags, template_tags

add_to_builtins(as_tags.__name__)
add_to_builtins(template_tags.__name__)


def render(contents, extra_context=None):
    return template.Template(contents).render(template.Context(extra_context))


class AsTag(TestCase):

    def test_simple(self):
        """
        A tag with named arguments works with or without the argument as long
        as a default value is set.
        """
        self.assertEqual(render('{% fish_as as out %}-{{ out }}'), '-fish')
        self.assertEqual(render('{% another_fish_as as out %}-{{ out }}'), '-fish')

    def test_optional(self):
        """
        A tag with named arguments works with or without the argument as long
        as a default value is set.
        """
        self.assertEqual(render('{% maybe_as %}-{{ out }}'), 'maybe-')
        self.assertEqual(render('{% maybe_as as out %}-{{ out }}'), '-maybe')

    def test_as_output(self):
        """
        A tag with named arguments works with or without the argument as long
        as a default value is set.
        """
        self.assertEqual(render('{% output_as 1 %}-{{ out }}'), '1-')
        self.assertEqual(render('{% output_as 1 as out %}-{{ out }}'),
                         'yes_as-1')

    def test_as_default(self):
        """
        A default variable name can be used (which will force ``as_required``
        to ``False``).
        """
        self.assertEqual(render('{% default_as %}...{{ snake }}'), '...hisss')

    def test_invalid_as_name(self):
        """
        A tag can't be create with an as_name which matches a named argument.
        """

        def make_bad_tag():
            class BadTag(ttag.helpers.AsTag):
                as_ = ttag.Arg(named=True)

        self.assertRaises(template.TemplateSyntaxError, make_bad_tag)


@override_settings(TEMPLATE_DIRS=[path.join(path.dirname(__file__), 'templates')])
class TemplateTag(TestCase):

    def test_simple(self):
        """
        A tag with named arguments works with or without the argument as long
        as a default value is set.
        """
        self.assertRaises(template.TemplateSyntaxError, render, '{% go %}')
        self.assertEqual(render('{% go using "the_flow.html" %}'), 'yeah')

    def test_optional(self):
        today = datetime.datetime.today()
        self.assertEqual(render('{% ask "What date is it?" %}'), today.strftime('%h %d, %Y'))
        self.assertEqual(render('{% ask "What date is it" using "long.html" %}'), today.strftime('%B %d, %Y'))
        self.assertEqual(render('{% ask "What the frak?" %}'), "")

    def test_with_argument(self):
        self.assertEqual(render('{% do %}'), 'done')
        self.assertEqual(render('{% do it "now.html" %}'), 'already done')
