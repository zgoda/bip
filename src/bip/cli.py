import difflib
import sys

import click
import keyring
from dotenv import find_dotenv, load_dotenv
from flask.cli import FlaskGroup, with_appcontext
from flask_migrate.cli import db as migrate_ops
from texttable import Texttable

from . import make_app
from .data import Filter, Sort, user, category, page, directory
from .ext import db
from .models import ChangeRecord, ChangeType
from .utils.cli import ACTIVITY_NAME_MAP, SYS_NAME, login_user, print_table
from .utils.text import yesno

migrate_ops.help = 'Operacje na bazie danych aplikacji'


def create_app(_unused):  # pragma: no cover
    return make_app('dev')


@click.group(
    cls=FlaskGroup, create_app=create_app, help='Zarządzanie aplikacją BIP'
)
def cli():  # pragma: no cover
    pass


@migrate_ops.command(name='init', help='Initialize missing database objects')
@with_appcontext
def initdb():  # pragma: no cover
    db.create_all()


@migrate_ops.command(name='clear', help='Remove all database objects')
@with_appcontext
def cleardb():  # pragma: no cover
    db.drop_all()


@migrate_ops.command('recreate', help='Recreate all database objects from scratch')
@with_appcontext
def recreatedb():  # pragma: no cover
    db.drop_all()
    db.create_all()


@cli.group(name='user', help='Zarządzanie użytkownikami')
def user_ops():  # pragma: no cover
    pass


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
        table = Texttable()
        table.set_deco(Texttable.HEADER | Texttable.BORDER)
        table.set_cols_align(['r', 'l', 'l', 'c', 'c'])
        table.set_cols_dtype(['i', 't', 't', 't', 't'])
        table.header(['ID', 'Nazwa', 'Email', 'Aktywne', 'Administrator'])
        for user_obj in q.all():
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
def user_change(name, email, active, user_name):
    if email is not None:
        email = email.strip()
    if not any([email, active]):
        click.echo('nic do zrobienia')
        sys.exit(0)
    user_obj = login_user(user_name)
    if user_obj.name != name:
        user_obj = user.by_name(name)
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
@click.option(
    '--user', '-u', 'user_name', required=True, help='Nazwa konta użytkownika'
)
def user_info(user_name):
    password = keyring.get_password(SYS_NAME, user_name)
    if password:
        click.echo(f'użytkownik {user_name}: zalogowany')
    else:
        click.echo(f'użytkownik {user_name}: niezalogowany')


@cli.group(name='category', help='Zarządzanie kategoriami w menu')
def category_ops():  # pragma: no cover
    pass


@category_ops.command(name='list', help='Wyświetl listę kategorii')
@click.option(
    '--active/--inactive', default=None,
    help='Wyświetl tylko aktywne lub nieaktywne (domyślnie: wszystkie)',
)
def category_list(active):
    cat_prop = ACTIVITY_NAME_MAP[active]
    sort = [
        Sort('menu_order'), Sort('title')
    ]
    filters = None
    if active is not None:
        filters = [Filter(field='active', op='eq', value=True)]
    q = category.query(sort, filters)
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
        for cat_obj in q.all():
            table.add_row([
                cat_obj.pk, cat_obj.title,
                yesno(cat_obj.directory is not None), cat_obj.menu_order,
                yesno(cat_obj.active),
            ])
        print_table(table)


@category_ops.command(name='create', help='Utwórz nową kategorię w menu')
@click.option('--title', '-t', required=True, help='Tytuł kategorii')
@click.option(
    '--directory/--no-directory', 'is_directory', default=False,
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
    '--user', '-u', 'user_name', required=True,
    help='Wykonaj operację jako wskazany użytkownik',
)
def category_create(title, is_directory, active, order, user_name):
    user_obj = login_user(user_name)
    c_page = page.create(
        title=title, created_by=user_obj, active=active, text=title, save=False,
    )
    c_dir = None
    if is_directory:
        c_dir = directory.create(
            title=title, created_by=user_obj, active=active, page=c_page, save=False
        )
        db.session.add(c_dir)
    db.session.add(c_page)
    c_menuitem = category.create(
        directory=c_dir, page=c_page, title=title, active=active, menu_order=order,
        save=False,
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
@click.option('--category', '-c', 'cat_pk', type=int, help='ID kategorii do zmiany')
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
    '--user', '-u', 'user_name', required=True,
    help='Wykonaj operację jako wskazany użytkownik',
)
def category_change(cat_pk, description, title, active, order, user_name):
    user_obj = login_user(user_name)
    cat_obj = category.get(cat_pk)
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
def directory_ops():  # pragma: no cover
    pass


def main():
    load_dotenv(find_dotenv())
    cli()
