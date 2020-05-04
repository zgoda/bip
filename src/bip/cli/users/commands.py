import sys

import click
import keyring
from flask import current_app
from flask.cli import with_appcontext

from ...display import ColumnOverride, DisplayMeta
from ...models import User
from ...utils.cli import (
    ACTIVITY_NAME_MAP, SYS_NAME, create_table, login_user, print_table,
)
from ...utils.text import yesno

user_ops = click.Group(name='user', help='Zarządzanie kontami użytkowników')


@user_ops.command(name='login', help='Zaloguj użytkownika i zachowaj dane logowania')
@click.option(
    '--name', '-n', 'user_name', required=True, help='Nazwa konta użytkownika'
)
@click.option(
    '--clear', '-c', is_flag=True, default=False,
    help='Wyczyść dane logowania (domyślnie: NIE)',
)
@with_appcontext
def user_login(user_name: str, clear: bool):
    login_user(user_name, admin=False)
    if clear:
        keyring.delete_password(SYS_NAME, user_name)
        click.echo(f'dane logowania użytkownika {user_name} zostały usunięte')
    else:
        click.echo(f'dane logowania użytkownika {user_name} zostały zapisane')


@user_ops.command(name='list', help='Wyświetl listę użytkowników')
@click.option(
    '--active/--inactive', default=None,
    help='Wyświetl tylko aktywne lub nieaktywne (domyślnie: wszystkie)',
)
@with_appcontext
def user_list(active: bool):
    acct_prop = ACTIVITY_NAME_MAP[active]
    q = User.select()
    if active is not None:
        q = q.where(User.active == active)
    q = q.order_by(User.name)
    acct_count = q.count()
    if acct_count == 0:
        click.echo('Nie ma żadnych kont użytkowników')
        sys.exit(0)
    click.echo(f'Znaleziono {acct_count}, wyświetlanie: {acct_prop}')
    col_overrides = {
        'pk': ColumnOverride(title='ID'),
        'name': ColumnOverride(title='Nazwa'),
        'email': ColumnOverride(title='Email'),
        'active': ColumnOverride(title='Aktywne'),
        'admin': ColumnOverride(title='Administrator'),
    }
    col_names = ['pk', 'name', 'email', 'active', 'admin']
    columns = DisplayMeta(
        User, columns=col_names
    ).cli_list_columns(overrides=col_overrides)
    table = create_table(current_app.testing, columns)
    for user_obj in q:
        table.add_row([
            user_obj.pk, user_obj.name, user_obj.email,
            yesno(user_obj.active), yesno(user_obj.admin),
        ])
    print_table(table)


@user_ops.command(name='create', help='Zakładanie nowego konta użytkownika')
@click.option('--name', '-n', required=True, help='Nazwa konta użytkownika')
@click.password_option('--password', '-p', required=True, help='Hasło użytkownika')
@click.option('--email', '-e', required=False, help='Email użytkownika')
@click.option(
    '--active/--inactive', default=False,
    help='Czy konto ma być od razu aktywne (domyślnie: NIE)',
)
@click.option(
    '--admin/--regular', default=False,
    help='Czy konto ma mieć uprawnienia administracyjne (domyślnie: NIE)',
)
@click.option(
    '-u', '--user', 'user_name',
    help='Nazwa użytkownika wykonującego czynność',
)
@with_appcontext
def user_create(
            name: str, password: str, email: str, active: bool, admin: bool,
            user_name: str,
        ):
    if User.select().count() > 0:
        if not user_name:
            raise click.ClickException(
                'tylko dodanie pierwszego użytkownika nie wymaga logowania'
            )
        login_user(user_name, admin=True)
    user = User(
        name=name, email=email, active=active, admin=admin
    )
    user.set_password(password)
    user.save()
    click.echo(f'konto użytkownika {name} zostało założone')


@user_ops.command(name='change', help='Zmiana danych konta użytkownika')
@click.option(
    '--name', '-n', required=True,
    help='Nazwa konta użytkownika które ma zostać zmienione',
)
@click.option(
    '--email', '-e', default=None, required=False,
    help='Email użytkownika (domyślnie: bez zmiany)',
)
@click.option(
    '--active/--inactive', default=None,
    help='Zmiana aktywacji konta (domyślnie: bez zmiany)',
)
@click.option(
    '--user', '-u', 'user_name', required=True,
    help='Wykonaj operację jako wskazany użytkownik',
)
@with_appcontext
def user_change(name: str, email: str, active: bool, user_name: str):
    if email is not None:
        email = email.strip()
    if email is None and active is None:
        click.echo('nic do zrobienia')
        sys.exit(0)
    require_admin = name != user_name
    actor = login_user(user_name, admin=require_admin)
    if active is not None and not actor.admin:
        raise click.ClickException(
            'tylko administrator może aktywować konta użytkowników'
        )
    if actor.name != name:
        user_obj = User.get_or_none(User.name == name)
        if user_obj is None:
            raise click.ClickException(f'nie znaleziono konta użytkownika {name}')
    else:
        user_obj = actor
    if email:
        user_obj.email = email
    if active is not None:
        user_obj.active = active
    user_obj.save()
    click.echo(f'dane konta użytkownika {name} zostały zmienione')


@user_ops.command(name='info', help='Informacje o zalogowanym użytkowniku')
@click.option(
    '--user', '-u', 'user_name', required=True, help='Nazwa konta użytkownika'
)
def user_info(user_name: str):
    password = keyring.get_password(SYS_NAME, user_name)
    if password:
        click.echo(f'użytkownik {user_name}: zalogowany')
    else:
        click.echo(f'użytkownik {user_name}: niezalogowany')
