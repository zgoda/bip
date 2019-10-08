import shutil

import click
import keyring
from texttable import Texttable

from ..data import user
from ..models import User

SYS_NAME = 'bip'

ACTIVITY_NAME_MAP = {
    True: 'aktywne',
    False: 'nieaktywne',
    None: 'wszystkie',
}


def login_user(username: str, admin: bool = True) -> User:
    """Verify administrative user login.

    :param username: user account name
    :type username: str
    :param admin: require administrative privileges, defaults to True
    :type admin: bool, optional
    :raises click.ClickException: if credentials are not valid
    :return: logged in user object
    :rtype: :class:`~bip.models.User`
    """

    password = keyring.get_password(SYS_NAME, username)
    if not password:
        click.echo(f'użytkownik {username} nie ma zapisanego hasła w pęku kluczy')
        password = click.prompt('Hasło: ', hide_input=True)
    user_obj = user.by_name(username, admin=True)
    if not (user_obj and user_obj.check_password(password)):
        raise click.ClickException(
            'nieprawidłowe dane logowania lub niewystarczające uprawnienia - '
            f'nie znaleziono konta {username} lub nieprawidłowe hasło'
        )
    keyring.set_password(SYS_NAME, username, password)
    return user_obj


def print_table(table: Texttable):
    """Print table to terminal or to pager depending on table size.

    :param table: table to be printed
    :type table: :class:`~texttable.Texttable`
    """

    text = table.draw()
    num_rows = len(text.splitlines())
    if num_rows + 1 > shutil.get_terminal_size().lines:
        click.echo_via_pager(text)
    else:
        click.echo(text)
