import shutil

import click
import keyring
from texttable import Texttable

from ..models import User
from ..security import pwd_context

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
    :rtype: :class:`~models.User`
    """

    password = keyring.get_password(SYS_NAME, username)
    if not password:
        click.echo(f'użytkownik {username} nie ma zapisanego hasła w pęku kluczy')
        password = click.prompt('Hasło: ', hide_input=True)
    user_q = User.query.filter_by(name=username)
    if admin:
        user_q = user_q.filter_by(admin=True)
    user_obj = user_q.first()
    if not (user_obj and pwd_context.verify(password, user_obj.password)):
        raise click.ClickException(
            'nieprawidłowe dane logowania lub niewystarczające uprawnienia - '
            f'nie znaleziono konta {username} lub nieprawidłowe hasło'
        )
    keyring.set_password(SYS_NAME, username, password)
    return user_obj


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
