import re
from typing import Sequence

from jinja2.filters import do_truncate
from text_unidecode import unidecode

VALUE_YES = 'tak'
VALUE_NO = 'nie'

_punctuation_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def yesno(value: bool, capitalize: bool = True) -> str:
    """Return "yes" or "no" as textual representation of Boolean value in
    Polish. Returned string is capitalized by default.

    :param value: value to be represented
    :type value: bool
    :param capitalize: whether to capitalize output string, defaults to True
    :type capitalize: bool, optional
    :return: textual representation of Boolean value
    :rtype: str
    """
    ret = VALUE_YES if value else VALUE_NO
    if capitalize:
        return ret.capitalize()
    return ret


def slugify(text: str, delim: str = '-') -> str:
    """Create slug (url-safe ASCII representation) of given string.

    :param text: text to slugify
    :type text: str
    :param delim: delimiter, defaults to '-'
    :type delim: str, optional
    :return: slugified text
    :rtype: str
    """
    result = []
    for word in _punctuation_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return delim.join(result)


def truncate_string(s: str, length: int) -> str:
    """Truncate string at word boundary.

    :param s: string to be truncated
    :type s: str
    :param length: max length of result string
    :type length: int
    :return: truncated text
    :rtype: str
    """
    return do_truncate(None, s, length, leeway=5)


def pluralize(value: int, plural_forms: Sequence[str]) -> str:
    """Polish pluralization.

    :param value: item count
    :type value: int
    :param plural_forms: sequence of 3 pluralization forms (singular and 2
                         plurals)
    :type plural_forms: Sequence[str]
    :return: pluralized item literal
    :rtype: str
    """
    singular, plural_1, plural_2 = plural_forms
    if str(value)[-1] == '1' and len(str(abs(value))) == 1:  # skipcq: PYL-R1705
        return f'{value} {singular}'
    elif str(value)[-1:] in ('2', '3', '4') and str(value)[-2:-1] != '1':
        return f'{value} {plural_1}'
    return f'{value} {plural_2}'
