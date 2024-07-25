import re

try:
    from django.utils.encoding import force_str
except ImportError:  # Django <1.8
    from django.utils.encoding import force_unicode as force_text

_split_single = r"""
    ([^\s",]*"(?:[^"\\]*(?:\\.[^"\\]*)*)"[^\s,]*|
     [^\s',]*'(?:[^'\\]*(?:\\.[^'\\]*)*)'[^\s,]*|
     [^\s,]+)
"""
_split_multi = r"""%s(?:\s*,\s*%s)*""" % (_split_single, _split_single)
_split_single_re = re.compile(_split_single, re.VERBOSE)
_split_multi_re = re.compile(_split_multi, re.VERBOSE)

CLASS_NAME_RE = re.compile(r'(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))')


def smarter_split(input):
    input = force_str(input)
    for multi_match in _split_multi_re.finditer(input):
        hit = []
        for single_match in _split_single_re.finditer(multi_match.group(0)):
            hit.append(single_match.group(0))
        if len(hit) == 1:
            yield hit[0]
        else:
            yield hit


def get_default_name(class_name):
    return CLASS_NAME_RE.sub(r'_\1', class_name).lower().strip('_')
