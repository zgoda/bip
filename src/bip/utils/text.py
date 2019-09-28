def yesno(value: bool, capitalize: bool = True) -> str:
    """Return "yes" or "no" as textual representation of Boolean value.
    Returned string is capitalized by default.

    :param value: value to be represented as `str`
    :type value: bool
    :param capitalize: whether to capitalize output string, defaults to True
    :type capitalize: bool, optional
    :return: textual representation of Boolean value
    :rtype: str
    """

    if value:
        ret = 'tak'
    else:
        ret = 'nie'
    if capitalize:
        return ret.capitalize()
    return ret
