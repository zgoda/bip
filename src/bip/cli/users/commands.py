import sys

import click
import keyring
from flask import current_app
from flask.cli import with_appcontext

from ...data import Filter, Sort, user
from ...ext import db
from ...utils.cli import (
    ACTIVITY_NAME_MAP, SYS_NAME, ColSpec, create_table, login_user, print_table,
)
from ...utils.text import yesno

user_ops = click.Group(name='user', help='Zarządzanie kontami użytkowników')


@user_ops.command(name='login', help='Zaloguj użytkownika i zachowaj dane logowania')
@click.option('--user-name', '-u', required=True, help='Nazwa konta użytkownika')
@click.option(
    '--password', '-p', prompt=True, hide_input=True, required=True,
    help='Hasło użytkownika',
)
@click.option(
    '--clear', '-c', is_flag=True, default=False,
    help='Wyczyść dane logowania (domyślnie: NIE)',
)
def user_login(user_name, password, clear):
    login_user(user_name, admin=False)
    if clear:
        keyring.delete_password(SYS_NAME, user_name)
        click.echo(f'dane logowania użytkownika {user_name} zostały usunięte')
    else:
        keyring.set_password(SYS_NAME, user_name, password)
        click.echo(f'dane logowania użytkownika {user_name} zostały zapisane')


@user_ops.command(name='list', help='Wyświetl listę użytkowników')
@click.option(
    '--active/--inactive', default=None,
    help='Wyświetl tylko aktywne lub nieaktywne (domyślnie: wszystkie)',
)
@with_appcontext
def user_list(active):
    acct_prop = ACTIVITY_NAME_MAP[active]
    filters = None
    if active is not None:
        filters = [Filter(field='active', op='eq', value=active)]
    q = user.query(sort=[Sort(field='name')], filters=filters)
    acct_count = q.count()
    if acct_count == 0:
        click.echo('Nie ma żadnych kont użytkowników')
    else:
        click.echo(f'Znaleziono {acct_count}, wyświetlanie: {acct_prop}')
        columns = [
            ColSpec('r', 'i', 'ID'),
            ColSpec('l', 't', 'Nazwa'),
            ColSpec('l', 't', 'Email'),
            ColSpec('c', 't', 'Aktywne'),
            ColSpec('c', 't', 'Administrator'),
        ]
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
@with_appcontext
def user_create(name, password, email, active, admin):
    user.create(
        name=name, password=password, email=email, active=active, admin=admin
    )
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
def user_change(name, email, active, user_name):
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
        user_obj = user.by_name(name)
        if user_obj is None:
            raise click.ClickException(f'nie znaleziono konta użytkownika {name}')
    else:
        user_obj = actor
    if email:
        user_obj.email = email
    if active is not None:
        user_obj.active = active
    db.session.add(user_obj)
    db.session.commit()
    click.echo(f'dane konta użytkownika {name} zostały zmienione')


@user_ops.command(name='info', help='Informacje o zalogowanym użytkowniku')
@click.option(
    '--user', '-u', 'user_name', required=True, help='Nazwa konta użytkownika'
)
def user_info(user_name):
    password = keyring.get_password(SYS_NAME, user_name)
    if password:
        click.echo(f'użytkownik {user_name}: zalogowany')
    else:
        click.echo(f'użytkownik {user_name}: niezalogowany')
