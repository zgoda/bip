import click
import keyring

from ..models import User
from ..security import pwd_context

SYS_NAME = 'bip'

ACTIVITY_NAME_MAP = {
    True: 'aktywne',
    False: 'nieaktywne',
    None: 'wszystkie',
}


def user_login(username):
    password = keyring.get_password(SYS_NAME, username)
    if not password:
        click.echo(f'użytkownik {username} nie ma zapisanego hasła w pęku kluczy')
        password = click.prompt('Hasło: ', hide_input=True)
    user_obj = User.query.filter_by(name=username).first()
    if not (user_obj and pwd_context.verify(password, user_obj.password)):
        raise click.ClickException(
            'nieprawidłowe dane logowania - '
            'nie znaleziono użytkownika lub nieprawidłowe hasło'
        )
    keyring.set_password(SYS_NAME, username, password)
    return user_obj


def yesno(value, capitalize=True):
    if value:
        ret = 'tak'
    else:
        ret = 'nie'
    if capitalize:
        return ret.capitalize()
    return ret
