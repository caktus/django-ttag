import datetime

from django.test import TestCase
from django import template

import ttag
from ttag.tests.setup import tags, models

template.add_to_builtins(tags.__name__)


def render(contents, extra_context=None):
    return template.Template(contents).render(template.Context(extra_context))


class TagExecutionTests(TestCase):

    def test_default(self):
        """
        A tag with named arguments works with or without the argument as long
        as a default value is set.
        """
        self.assertEqual(render('{% named_arg %}'),
                         'The limit is %d' %
                         tags.NamedArg._meta.args['limit'].default)

        # Reset the limit tag to have no default (and be required, which is set
        # to False if a default was given.
        tags.NamedArg._meta.args['limit'].default = None
        tags.NamedArg._meta.args['limit'].required = True

        self.assertRaises(template.TemplateSyntaxError, render,
            '{% named_arg %}')

    def test_named(self):
        """
        Standard named argument syntax is ``{% tag arg value %}``
        """
        self.assertEqual(render('{% named_arg limit 200 %}'),
                         'The limit is 200')
        self.assertRaises(template.TemplateSyntaxError, template.Template,
                          '{% named_arg limit=25 %}')

    def test_named_keyword(self):
        self.assertEqual(render('{% named_keyword_arg limit=100 %}'),
                         'The limit is 100')
        self.assertRaises(template.TemplateSyntaxError, template.Template,
                          "{% named_keyword_arg limit 15 %}")

    def test_handle_args(self):
        """tags with no arguments take no arguments"""
        self.assertRaises(template.TemplateSyntaxError, template.Template,
                          '{% no_argument this fails %}')

    def test_constant_tag(self):
        """tags with no arguments take no arguments"""
        self.assertEqual(render('{% constant 1 to 2 %}'), '1 - 2')
        self.assertRaises(template.TemplateSyntaxError, template.Template,
                          '{% constant 1 t 2 %}', {'t': 'to'})

    def test_block_tag(self):
        """tags with a block meta option"""
        self.assertEqual(render('{% repeat 5 %}a{% done %}'), 'aaaaa')

    def test_multiple_block_tag(self):
        """tags with a block meta option"""
        self.assertEqual(render('{% repeat_with_empty 5 %}a{% empty %}b{% stop %}'), 'aaaaa')
        self.assertEqual(render('{% repeat_with_empty 0 %}a{% empty %}b{% stop %}'), 'b')


def build_invalid_positional_optional():

    class Tag(ttag.Tag):
        start = ttag.Arg(required=False)
        end = ttag.Arg()


class PositionalTest(TestCase):

    def test_positional(self):
        """
        Test that positional arguments work.
        """
        self.assertEqual(render('{% positional 10 %}'), u"10")

        self.assertRaises(template.TemplateSyntaxError, render,
                          '{% positional %}')
        self.assertRaises(template.TemplateSyntaxError, render,
                          '{% positional limit 10 %}')

    def test_positional_mixed(self):
        """
        Test that positional arguments work, mixed with named arguments.
        """
        self.assertEqual(render('{% positional_mixed 1 as a%}x{{ a }}'), 'x1')
        self.assertEqual(render('{% positional_mixed var as a%}x{{ a }}',
                                {'var': '2'}), 'x2')

    def test_positional_mixedkw(self):
        """
        Test that positional arguments work, mixed with keyword arguments.
        """
        self.assertEqual(render('{% positional_mixedkw 1 default=9 %}'), '1')
        self.assertEqual(render('{% positional_mixedkw var default=9 %}',
                                {'var': None}), '9')
        self.assertEqual(render('{% positional_mixedkw default=9 %}'), '9')

    def test_positional_optional(self):
        """
        Test that optional positional arguments work.
        """
        self.assertEqual(render('{% positional_optional 2 %}'), '0,1')
        self.assertEqual(render('{% positional_optional_mixed 10 step 2 %}'),
                         '0,2,4,6,8')

    def test_optional_last(self):
        """
        Test that an error is raised if optional positional arguments are
        followed by required ones.
        """
        self.assertRaises(template.TemplateSyntaxError,
                          build_invalid_positional_optional)


class TestArgumentTypes(TestCase):

    def test_model_instance_arg(self):
        content = '{% argument_type url object %}'
        object = models.Link(url='http://bing.com')
        self.assertEqual(render(content, {'object': object}),
                         unicode(object))

        self.assertRaises(ttag.TagValidationError, render, content,
                          {'object': int()})

        # Fail if the variable isn't in the context.
        self.assertRaises(ttag.TagValidationError, render, content)

    def test_integer_arg(self):
        self.assertEqual(render('{% argument_type age 101 %}'), '101')
        self.assertEqual(render('{% argument_type age a %}', {'a': 99}), '99')

        # IntegerArg.clean calls int(value), so string integers should be
        # converted.
        self.assertEqual(render('{% argument_type age "23" %}'), '23')
        self.assertEqual(render('{% argument_type age a %}', {'a': '7'}), '7')

        # Fail if value or variable can't be resolved as an integer.
        self.assertRaises(ttag.TagValidationError, render,
                          '{% argument_type age "7b" %}')
        self.assertRaises(ttag.TagValidationError, render,
                          '{% argument_type age age %}', {'age': 'NaN'})

        # Fail if the variable isn't in the context.
        self.assertRaises(ttag.TagValidationError, render,
                          '{% argument_type age age %}')

    def test_string_arg(self):
        # Ensure both single quotes and double quotes work.
        self.assertEqual(render('{% argument_type name "alice" %}'), 'alice')
        self.assertEqual(render("{% argument_type name 'bob' %}"), 'bob')

        # Ensure a context variable works.
        self.assertEqual(render("{% argument_type name dave %}",
                                {'dave': 'Dave'}),
                         'Dave')

        # Values are cast to unicode.
        class Name(object):
            
            def __init__(self, name):
                self.name = name

            def __unicode__(self):
                return self.name

        self.assertEqual(render('{% argument_type name dave %}',
                                {'dave': Name('dave')}), 'dave')

        # Fail if the variable isn't in the context.
        self.assertRaises(ttag.TagValidationError, render,
                          '{% argument_type name dave %}')

    def test_datetime_arg(self):
        self.assertEqual(render('{% argument_type datetime dt %}',
                                {'dt': datetime.datetime(2010, 1, 9,
                                                         22, 33, 47)}),
                         '2010-01-09 22:33:47')

        # Fail if variable isn't a datetime.
        self.assertRaises(ttag.TagValidationError, render,
                          '{% argument_type datetime dt %}', {'dt': 'NaN'})

        # Fail if the variable isn't in the context.
        self.assertRaises(ttag.TagValidationError, render,
                          '{% argument_type datetime dt %}')

    def test_date_arg(self):
        self.assertEqual(render('{% argument_type date d %}',
                                {'d': datetime.date(2010, 1, 9)}),
                         '2010-01-09')

        # Fail if variable isn't a datetime.
        self.assertRaises(ttag.TagValidationError, render,
                          '{% argument_type date d %}', {'d': 'NaN'})

        # Fail if the variable isn't in the context.
        self.assertRaises(ttag.TagValidationError, render,
                          '{% argument_type date d %}')

    def test_time_arg(self):
        self.assertEqual(render('{% argument_type time t %}',
                                {'t': datetime.time(22, 33, 47)}),
                         '22:33:47')

        # Fail if variable isn't a datetime.
        self.assertRaises(ttag.TagValidationError, render,
                          '{% argument_type time t %}', {'t': 'NaN'})

        # Fail if the variable isn't in the context.
        self.assertRaises(ttag.TagValidationError, render,
                          '{% argument_type time t %}')

    def test_flag_arg(self):
        self.assertEqual(render('{% argument_type %}'), '')
        self.assertEqual(render('{% argument_type flag %}'), 'flag_is_set')

    def test_multi_arg(self):
        self.assertEqual(render('{% dot_combine 1 2 3 4 %}'), '1.2.3.4')
        self.assertEqual(
            render('{% dot_combine_default "a" b "c" default "X" %}',
                   {'b': None}), 'a.X.c')


class KeywordsArgTest(TestCase):
    compact_kwargs = ' "file.html" with foo=x bar=2 %}'
    verbose_kwargs = ' "file.html" with x as foo and 2 as bar %}'
    mixed_kwargs = ' "file.html" with bar=2 x as foo and baz=3 %}'

    def test_not_required(self):
        self.assertEqual(render('{% include_compact "file.html" %}'),
                         'including file.html')
        self.assertEqual(render('{% include_verbose "file.html" %}'),
                         'including file.html')
        self.assertEqual(render('{% include_mixed "file.html" %}'),
                         'including file.html')

    def test_compact(self):
        self.assertEqual(
            render('{% include_compact' + self.compact_kwargs, {'x': 1}),
            'including file.html with bar = 2 and foo = 1'
        )

    def test_compact_invalid(self):
        self.assertRaises(
            template.TemplateSyntaxError, render,
            '{% include_compact "file.html" with foo=1 and bar=2 %}'
        )
        self.assertRaises(
            template.TemplateSyntaxError, render,
            '{% include_compact' + self.verbose_kwargs
        )
        self.assertRaises(
            template.TemplateSyntaxError, render,
            '{% include_compact' + self.mixed_kwargs
        )

    def test_verbose(self):
        self.assertEqual(
            render('{% include_verbose' + self.verbose_kwargs, {'x': 1}),
            'including file.html with bar = 2 and foo = 1'
        )

    def test_verbose_invalid(self):
        self.assertRaises(
            template.TemplateSyntaxError, render,
            '{% include_verbose' + self.compact_kwargs
        )
        self.assertRaises(
            template.TemplateSyntaxError, render,
            '{% include_verbose' + self.mixed_kwargs
        )

    def test_mixed(self):
        self.assertEqual(
            render('{% include_mixed' + self.mixed_kwargs, {'x': 1}),
            'including file.html with bar = 2 and baz = 3 and foo = 1'
        )

    def test_duplicate_key(self):
        self.assertRaises(
            template.TemplateSyntaxError, render,
            '{% include_compact "file.html" with foo=1 foo=2 %}'
        )
        self.assertRaises(
            template.TemplateSyntaxError, render,
            '{% include_verbose "file.html" with 1 as foo and 2 as foo %}'
        )
        self.assertRaises(
            template.TemplateSyntaxError, render,
            '{% include_mixed "file.html" with foo=1 2 as foo %}'
        )

    def test_loop(self):
        self.assertEqual(render('|{% for i in "abc" %}{% keywords_echo '
                                'test=forloop.counter %}|{% endfor %}'),
                         '|test: 1|test: 2|test: 3|')
