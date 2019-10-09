import difflib
from typing import List

VALUE_YES = 'tak'
VALUE_NO = 'nie'


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
    from_lines = from_str.splitlines(keepends=True)
    to_lines = to_str.splitlines(keepends=True)
    for line in difflib.ndiff(from_lines, to_lines):
        line = line.strip()
        if line[0] in ('+', '-'):
            changes.append(line)
    return changes
