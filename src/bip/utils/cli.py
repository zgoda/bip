import shutil
from collections import namedtuple
from typing import List

import click
import keyring
from texttable import Texttable

from ..models import User

SYS_NAME = 'bip'

ACTIVITY_NAME_MAP = {
    True: 'aktywne',
    False: 'nieaktywne',
    None: 'wszystkie',
}


class ColAlign:
    """Column alignment enum
    """
    right = 'r'
    center = 'c'
    left = 'l'


class ColDataType:
    """Column data type enum
    """
    auto = 'a'
    text = 't'
    float = 'f'  # noqa: A003
    exp = 'e'
    int = 'i'  # noqa: A003


ColSpec = namedtuple('ColSpec', ['align', 'dtype', 'title'])


def login_user(username: str, admin: bool = True) -> User:
    """Verify user login.

    :param username: user account name
    :type username: str
    :param admin: require administrative privileges, defaults to True
    :type admin: bool, optional
    :raises click.ClickException: if credentials are not valid
    :return: logged in user object
    :rtype: :class:`~bip.models.User`
    """

    password = keyring.get_password(SYS_NAME, username)
    if not password:  # pragma: no cover
        click.echo(f'użytkownik {username} nie ma zapisanego hasła w pęku kluczy')
        password = click.prompt('Hasło', hide_input=True)
    if admin:
        user_obj = User.get_or_none(
            User.name == username & User.admin == admin
        )
    else:
        user_obj = User.get_or_none(User.name == username)
    if not (user_obj and user_obj.check_password(password)):
        raise click.ClickException(
            'nieprawidłowe dane logowania lub niewystarczające uprawnienia - '
            f'nie znaleziono konta {username} lub nieprawidłowe hasło'
        )
    keyring.set_password(SYS_NAME, username, password)
    return user_obj


def create_table(is_testing: bool, cols: List[ColSpec]) -> Texttable:
    """Create table for term display. The table has unlimited size if
    application is in testing state, otherwise term size.

    :param is_testing: flag whether application is in testing state
    :type is_testing: bool
    :param cols: list of columns for the table
    :type cols: List[ColSpec]
    :return: table object
    :rtype: :class:`~texttable.Texttable`
    """
    if is_testing:
        width = 0
    else:  # pragma: no cover
        width = shutil.get_terminal_size().columns
    table = Texttable(max_width=width)
    table.set_deco(Texttable.HEADER | Texttable.BORDER)
    align, dtypes, titles = [], [], []
    for col in cols:
        align.append(col.align)
        dtypes.append(col.dtype)
        titles.append(col.title)
    table.set_cols_align(align)
    table.set_cols_dtype(dtypes)
    table.header(titles)
    return table


def print_table(table: Texttable):
    """Print table to terminal or to pager depending on table size.

    :param table: table to be printed
    :type table: :class:`~texttable.Texttable`
    """

    text = table.draw()
    num_rows = len(text.splitlines())
    if num_rows + 1 > shutil.get_terminal_size().lines:  # pragma: no cover
        click.echo_via_pager(text)
    else:
        click.echo(text)
