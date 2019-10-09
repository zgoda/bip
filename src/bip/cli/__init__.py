import click
from dotenv import find_dotenv, load_dotenv
from flask.cli import FlaskGroup
from flask_migrate.cli import db as migrate_ops
from texttable import Texttable

from .. import make_app
from ..data import Filter, Sort, category, change, directory, page
from ..ext import db
from ..utils.cli import ACTIVITY_NAME_MAP, login_user, print_table
from ..utils.text import text_changes, yesno
from .database import commands as db_commands
from .users import commands as user_commands

migrate_ops.help = 'Operacje na bazie danych aplikacji'


def create_app(_unused):  # pragma: no cover
    return make_app('dev')


@click.group(
    cls=FlaskGroup, create_app=create_app, help='Zarządzanie aplikacją BIP'
)
def cli():  # pragma: no cover
    pass


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
        for cat_obj in q:
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
    changes = []
    msg = 'utworzono'
    ctype = 'created'
    changes.append(change.record(c_page, ctype, user_obj, msg))
    if c_dir is not None:
        changes.append(
            change.record(c_dir, ctype, user_obj, msg)
        )
    changes.append(
        change.record(c_menuitem, ctype, user_obj, msg)
    )
    db.session.add_all(changes)
    db.session.commit()
    click.echo(f'kategoria {title} została utworzona')


@category_ops.command(name='change', help='Zmień dane kategorii w menu')
@click.option('--category', '-c', 'cat_pk', type=int, help='ID kategorii do zmiany')
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
def category_change(cat_pk, title, active, order, user_name):
    user_obj = login_user(user_name)
    cat_obj = category.get(cat_pk)
    if cat_obj is None:
        raise click.ClickException(f'Nie znaleziono kategorii o ID {category}')
    orig_title = cat_obj.title
    changes = []
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
            change.record(
                cat_obj, 'updated', user_obj, description='\n'.join(changes)
            )
        )
        db.session.commit()
        click.echo(f'kategoria {orig_title} została zmieniona')
    else:
        click.echo(f'bez zmian kategorii {orig_title}')


@category_ops.command(name='description', help='Zmień opis kategorii w menu')
@click.option('--category', '-c', 'cat_pk', type=int, help='ID kategorii do zmiany')
@click.option(
    '--user', '-u', 'user_name', required=True,
    help='Wykonaj operację jako wskazany użytkownik',
)
def category_change_description(cat_pk, user_name):
    user_obj = login_user(user_name)
    cat_obj = category.get(cat_pk)
    if cat_obj is None:
        raise click.ClickException(f'Nie znaleziono kategorii o ID {category}')
    orig_description = cat_obj.description or ''
    new_description = click.edit(orig_description)
    data_diff = text_changes(orig_description, new_description)
    if data_diff:
        diff_s = '\n'.join(data_diff)
        change_msg = f'opis, diff:\n{diff_s}'
        cat_obj.description = new_description
        db.session.add(cat_obj)
        db.session.add(
            change.record(
                cat_obj, 'updated', user_obj, description='\n'.join(change_msg)
            )
        )
        db.session.commit()
        click.echo(f'opis kategorii {cat_obj.title} został zmieniony')
    else:
        click.echo(f'opis kategorii {cat_obj.title} bez zmian')


@cli.group(name='directory', help='Operacje na katalogach')
def directory_ops():  # pragma: no cover
    pass


cli.add_command(db_commands.migrate_ops, name='db')
cli.add_command(user_commands.user_ops)


def main():
    load_dotenv(find_dotenv())
    cli()