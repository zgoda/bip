import difflib
import re
from typing import List

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
    if value:
        ret = VALUE_YES
    else:
        ret = VALUE_NO
    if capitalize:
        return ret.capitalize()
    return ret


def text_changes(from_str: str, to_str: str) -> List[str]:
    """Generate a diff for the list of strings.

    :param from_str: left (existing)
    :type from_str: str
    :param to_str: right (incoming)
    :type to_str: str
    :return: list of differencies
    :rtype: List[str]
    """
    changes = []
    if not from_str.endswith('\n'):
        from_str = f'{from_str}\n'
    from_lines = from_str.splitlines(keepends=True)
    if not to_str.endswith('\n'):
        to_str = f'{to_str}\n'
    to_lines = to_str.splitlines(keepends=True)
    for line in difflib.ndiff(from_lines, to_lines):
        line = line.strip()
        if line and line[0] in ('+', '-'):
            changes.append(line)
    return changes


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
