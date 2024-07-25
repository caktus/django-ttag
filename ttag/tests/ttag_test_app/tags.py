import six
try:
    from django.utils.encoding import force_str
except ImportError:  # Django <1.8
    from django.utils.encoding import force_unicode as force_text

import ttag
from ttag.core import BaseTag, DeclarativeArgsMetaclass
from ttag.tests.ttag_test_app import models
from ttag.tests.ttag_test_app.templatetags.ttag_test import register


class SelfRegisteringMetaclass(DeclarativeArgsMetaclass):

    def __new__(cls, name, bases, attrs):
        cls = DeclarativeArgsMetaclass.__new__(cls, name, bases, attrs)
        parents = [b for b in bases if isinstance(b, DeclarativeArgsMetaclass)]
        if parents:
            register.tag(cls._meta.name, cls)
        return cls


@six.add_metaclass(SelfRegisteringMetaclass)
class TestTag(BaseTag):
    pass


class NamedArg(TestTag):
    limit = ttag.IntegerArg(default=5, named=True)

    def output(self, data):
        if 'limit' in data:
            return 'The limit is %d' % data['limit']
        return 'No limit was specified'


class NamedKeywordArg(NamedArg):
    limit = ttag.IntegerArg(keyword=True)


class NoArgument(TestTag):

    def output(self, data):
        return 'No arguments here'


class Positional(TestTag):
    limit = ttag.IntegerArg()

    def output(self, data):
        return '%s' % data['limit']


class PositionalMixed(TestTag):
    limit = ttag.IntegerArg(default=5)
    as_ = ttag.BasicArg(named=True)

    def render(self, context):
        data = self.resolve(context)
        context[data['as']] = data['limit']
        return ''


class PositionalMixedkw(TestTag):
    value = ttag.Arg(required=False, null=True)
    default = ttag.Arg(keyword=True)

    def output(self, data):
        return six.text_type(data.get('value') or data['default'])


class PositionalOptional(TestTag):
    start = ttag.IntegerArg()
    finish = ttag.IntegerArg(required=False)

    def output(self, data):
        if 'finish' in data:
            start, finish = data['start'], data['finish']
        else:
            start, finish = 0, data['start']
        return ','.join([str(i) for i in range(start, finish)])


class PositionalOptionalMixed(TestTag):
    start = ttag.IntegerArg()
    finish = ttag.IntegerArg(required=False)
    step = ttag.IntegerArg(named=True)

    def output(self, data):
        if 'finish' in data:
            start, finish = data['start'], data['finish']
        else:
            start, finish = 0, data['start']
        return ','.join([str(i) for i in range(start, finish, data['step'])])


class ArgumentType(TestTag):
    age = ttag.IntegerArg(required=False, named=True)
    name_ = ttag.StringArg(required=False, named=True)
    url = ttag.ModelInstanceArg(model=models.Link, required=False, named=True)
    date = ttag.DateArg(required=False, named=True)
    time = ttag.TimeArg(required=False, named=True)
    datetime = ttag.DateTimeArg(required=False, named=True)
    flag = ttag.BooleanArg()

    def output(self, data):
        order = 'name age url date time datetime'.split()
        values = [six.text_type(data[x]) for x in order if x in data]
        if 'flag' in data:
            values.append('flag_is_set')
        return u' '.join(values)


class Constant(TestTag):
    start = ttag.Arg()
    to = ttag.ConstantArg()
    finish = ttag.Arg()

    def output(self, data):
        return '%s - %s' % (data['start'], data['finish'])


class KeywordsEcho(TestTag):
    keywords = ttag.KeywordsArg()

    def output(self, data):
        keywords = data['keywords'].items()
        return ', '.join('%s: %s' % (key, value) for key, value in keywords)


class DotCombine(TestTag):
    args = ttag.MultiArg()

    def output(self, data):
        args = [force_str(arg) for arg in data['args']]
        return '.'.join(args)


class DotCombineDefault(DotCombine):
    default = ttag.Arg(named=True)

    def output(self, data):
        args = [arg and force_str(arg) or data['default']
                for arg in data['args']]
        return '.'.join(args)


class Repeat(TestTag):
    count = ttag.IntegerArg()

    class Meta:
        block = True
        end_block = 'done'

    def render(self, context):
        data = self.resolve(context)
        output = []
        for i in range(data['count']):
            context.push()
            output.append(self.nodelist.render(context))
            context.pop()
        return ''.join(output)


class RepeatWithEmpty(TestTag):
    count = ttag.IntegerArg()

    class Meta:
        block = {'empty': False}
        end_block = 'stop'

    def render(self, context):
        data = self.resolve(context)
        if not data['count']:
            return self.nodelist_empty.render(context)
        output = []
        for i in range(data['count']):
            context.push()
            output.append(self.nodelist.render(context))
            context.pop()
        return ''.join(output)


class BaseInclude(TestTag):
    """
    A tag for testing KeywordsArg.
    """

    def output(self, data):
        out = 'including %s' % data['template']
        if data.get('with'):
            with_bits = list(data['with'].items())
            with_bits.sort(key=lambda bit: bit[0])
            out += ' with %s' % ' and '.join(['%s = %s' % (k, v)
                                              for k, v in with_bits])
        return out


class IncludeCompact(BaseInclude):
    template = ttag.Arg()
    with_ = ttag.KeywordsArg(named=True, required=False)


class IncludeVerbose(BaseInclude):
    template = ttag.Arg()
    with_ = ttag.KeywordsArg(named=True, required=False, compact=False,
                             verbose=True)


class IncludeMixed(BaseInclude):
    template = ttag.Arg()
    with_ = ttag.KeywordsArg(named=True, required=False, verbose=True)
