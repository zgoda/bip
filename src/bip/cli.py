import difflib
import sys

import click
import keyring
from dotenv import find_dotenv, load_dotenv
from flask.cli import FlaskGroup, with_appcontext
from flask_migrate.cli import db as migrate_ops
from texttable import Texttable

from . import make_app
from .ext import db
from .models import (
    ChangeRecord, ChangeType, Directory, ObjectMenuItem, SubjectPage, User,
)
from .utils.cli import ACTIVITY_NAME_MAP, SYS_NAME, login_user, print_table
from .utils.text import yesno

migrate_ops.help = 'Operacje na bazie danych aplikacji'


def create_app(info):
    return make_app('dev')


@click.group(
    cls=FlaskGroup, create_app=create_app, help='Zarządzanie aplikacją BIP'
)
def cli():
    pass


@migrate_ops.command(name='init', help='Initialize missing database objects')
@with_appcontext
def initdb():
    db.create_all()


@migrate_ops.command(name='clear', help='Remove all database objects')
@with_appcontext
def cleardb():
    db.drop_all()


@migrate_ops.command('recreate', help='Recreate all database objects from scratch')
@with_appcontext
def recreatedb():
    db.drop_all()
    db.create_all()


@cli.group(name='user', help='Zarządzanie użytkownikami')
def user_ops():
    pass


@user_ops.command(name='login', help='Zaloguj użytkownika i zachowaj dane logowania')
@click.option('--user', '-u', required=True, help='Nazwa konta użytkownika')
@click.option(
    '--password', '-p', prompt=True, hide_input=True, required=True,
    help='Hasło użytkownika',
)
@click.option(
    '--clear', '-c', is_flag=True, default=False,
    help='Wyczyść dane logowania (domyślnie: NIE)',
)
def user_login(user, password, clear):
    user_obj = User.query.filter_by(name=user).first()
    if not (user_obj and user_obj.check_password(password)):
        raise click.ClickException(
            'nieprawidłowe dane logowania - '
            'nie znaleziono użytkownika lub nieprawidłowe hasło'
        )
    if clear:
        keyring.delete_password(SYS_NAME, user)
        click.echo(f'dane logowania użytkownika {user} zostały usunięte')
    else:
        keyring.set_password(SYS_NAME, user, password)
        click.echo(f'dane logowania użytkownika {user} zostały zapisane')


@user_ops.command(name='list', help='Wyświetl listę użytkowników')
@click.option(
    '--active/--inactive', default=None,
    help='Wyświetl tylko aktywne lub nieaktywne (domyślnie: wszystkie)',
)
def user_list(active):
    acct_prop = ACTIVITY_NAME_MAP[active]
    q = User.query
    if active is not None:
        q = q.filter(User.active.is_(active))
    acct_count = q.count()
    if acct_count == 0:
        click.echo('Nie ma żadnych kont użytkowników')
    else:
        click.echo(f'Znaleziono {acct_count}, wyświetlanie: {acct_prop}')
        table = Texttable()
        table.set_deco(Texttable.HEADER | Texttable.BORDER)
        table.set_cols_align(['r', 'l', 'l', 'c', 'c'])
        table.set_cols_dtype(['i', 't', 't', 't', 't'])
        table.header(['ID', 'Nazwa', 'Email', 'Aktywne', 'Administrator'])
        q = q.order_by(User.name)
        for user in q.all():
            table.add_row([
                user.pk, user.name, user.email, yesno(user.active), yesno(user.admin),
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
def user_create(name, password, email, active, admin):
    user = User(name=name, email=email, active=active, admin=admin)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
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
    '--user', '-u', required=True, help='Wykonaj operację jako wskazany użytkownik'
)
def user_change(name, email, active, user):
    if email is not None:
        email = email.strip()
    if not any([email, active]):
        click.echo('nic do zrobienia')
        sys.exit(0)
    login_user(user)
    user_obj = User.query.filter_by(name=name).first()
    if user_obj is None:
        raise click.ClickException(f'nie znaleziono konta użytkownika {name}')
    if email:
        user_obj.email = email
    if active is not None:
        user_obj.active = active
    db.session.add(user_obj)
    db.session.commit()
    click.echo(f'dane konta użytkownika {name} zostały zmienione')


@user_ops.command(name='info', help='Informacje o zalogowanym użytkowniku')
@click.option('--user', '-u', required=True, help='Nazwa konta użytkownika')
def user_info(user):
    password = keyring.get_password(SYS_NAME, user)
    if password:
        click.echo(f'użytkownik {user}: zalogowany')
    else:
        click.echo(f'użytkownik {user}: niezalogowany')


@cli.group(name='category', help='Zarządzanie kategoriami w menu')
def category_ops():
    pass


@category_ops.command(name='list', help='Wyświetl listę kategorii')
@click.option(
    '--active/--inactive', default=None,
    help='Wyświetl tylko aktywne lub nieaktywne (domyślnie: wszystkie)',
)
def category_list(active):
    cat_prop = ACTIVITY_NAME_MAP[active]
    q = ObjectMenuItem.query
    if active is not None:
        q = q.filter(ObjectMenuItem.active.is_(active))
    cat_count = q.count()
    if cat_count == 0:
        click.echo('Nie ma żadnych kategorii')
    else:
        click.echo(f'Znaleziono: {cat_count}, wyświetlanie: {cat_prop}')
        table = Texttable()
        table.set_deco(Texttable.HEADER | Texttable.BORDER)
        table.set_cols_align(['r', 'l', 'c', 'r', 'c'])
        table.set_cols_dtype(['i', 't', 't', 'i', 't'])
        table.header(['ID', 'Tytuł', 'Katalog', 'Kolejność', 'Aktywna'])
        q = q.order_by(ObjectMenuItem.menu_order, ObjectMenuItem.title)
        for category in q.all():
            table.add_row([
                category.pk, category.title,
                yesno(category.directory is not None), category.menu_order,
                yesno(category.active),
            ])
        print_table(table)


@category_ops.command(name='create', help='Utwórz nową kategorię w menu')
@click.option('--title', '-t', required=True, help='Tytuł kategorii')
@click.option(
    '--directory/--no-directory', default=False,
    help='Czy kategoria jest katalogiem (domyślnie: NIE)',
)
@click.option(
    '--active/--inactive', default=False,
    help='Czy kategoria ma być od razu aktywna (domyślnie: NIE)',
)
@click.option(
    '--order', '-o', type=int, default=None,
    help='Kolejność kategorii w menu (domyślnie: bez ustalania kolejności)',
)
@click.option(
    '--user', '-u', required=True, help='Wykonaj operację jako wskazany użytkownik'
)
def category_create(title, directory, active, order, user):
    user_obj = login_user(user)
    c_page = SubjectPage(
        title=title, created_by=user_obj, active=active, text=title
    )
    c_dir = None
    if directory:
        c_dir = Directory(title=title, created_by=user_obj, active=active, page=c_page)
        db.session.add(c_dir)
    db.session.add(c_page)
    c_menuitem = ObjectMenuItem(
        directory=c_dir, page=c_page, title=title, active=active, menu_order=order,
    )
    db.session.add(c_menuitem)
    db.session.flush()
    msg = 'utworzono'
    db.session.add(ChangeRecord.log_change(c_page, ChangeType.created, user_obj, msg))
    if c_dir is not None:
        db.session.add(
            ChangeRecord.log_change(c_dir, ChangeType.created, user_obj, msg)
        )
    db.session.add(
        ChangeRecord.log_change(c_menuitem, ChangeType.created, user_obj, msg)
    )
    db.session.commit()
    click.echo(f'kategoria {title} została utworzona')


@category_ops.command(name='change', help='Zmień dane kategorii w menu')
@click.option('--category', '-c', type=int, help='ID kategorii do zmiany')
@click.option(
    '--description', '-d', is_flag=True, default=False,
    help='Zmień opis kategorii (domyślnie: NIE); uruchamia zdefiniowany edytor tekstu',
)
@click.option('--title', '-t', default=None, help='Zmień tytuł kategorii')
@click.option(
    '--active/--inactive', default=None, help='Zmień stan aktywności kategorii',
)
@click.option(
    '--order', '-o', type=int, default=None, help='Zmień kolejność kategorii w menu',
)
@click.option(
    '--user', '-u', required=True, help='Wykonaj operację jako wskazany użytkownik'
)
def category_change(category, description, title, active, order, user):
    user_obj = login_user(user)
    cat_obj = ObjectMenuItem.query.get(category)
    if cat_obj is None:
        raise click.ClickException(f'Nie znaleziono kategorii o ID {category}')
    orig_title = cat_obj.title
    changes = []
    if description:
        orig_description = cat_obj.description or ''
        new_description = click.edit(orig_description)
        if new_description:
            data_diff = list(
                difflib.unified_diff(
                    orig_description.splitlines(keepends=True),
                    new_description.splitlines(keepends=True),
                )
            )
            if data_diff:
                diff_s = '\n'.join(data_diff)
                changes.append(f'opis, diff:\n{diff_s}')
                cat_obj.description = new_description
    else:
        if title is not None:
            title = title.strip()
        if title:
            changes.append(f'tytuł: {cat_obj.title} -> {title}')
            cat_obj.title = title
        if active is not None:
            changes.append(f'aktywna: {yesno(cat_obj.active)} -> {yesno(active)}')
            cat_obj.active = active
        if order is not None:
            changes.append(f'kolejność: {cat_obj.menu_order} -> {order}')
            cat_obj.menu_order = order
    if changes:
        db.session.add(cat_obj)
        db.session.add(
            ChangeRecord.log_change(
                cat_obj, ChangeType.updated, user_obj, description='\n'.join(changes)
            )
        )
        db.session.commit()
        click.echo(f'kategoria {orig_title} została zmieniona')
    else:
        click.echo(f'bez zmian kategorii {orig_title}')


@cli.group(name='directory', help='Operacje na katalogach')
def directory_ops():
    pass


def main():
    load_dotenv(find_dotenv())
    cli()
