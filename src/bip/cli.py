import click
import keyring
from dotenv import find_dotenv, load_dotenv
from flask.cli import FlaskGroup, with_appcontext
from flask_migrate.cli import db as migrate_ops

from . import make_app
from .models import User, db, Directory, SubjectPage, ObjectMenuItem
from .security import pwd_context

migrate_ops.help = 'Operacje na bazie danych aplikacji'

SYS_NAME = 'bip'


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


@cli.command(name='login', help='Zaloguj użytkownika i zachowaj dane logowania')
@click.option('--user', '-u', required=True, help='Nazwa konta użytkownika')
@click.option(
    '--password', '-p', prompt=True, hide_input=True, required=True,
    help='Hasło użytkownika',
)
def login(user, password):
    user_obj = User.query.filter_by(name=user).first()
    if not (user_obj and pwd_context.verify(password, user_obj.password)):
        raise click.ClickException(
            'nieprawidłowe dane logowania - '
            'nie znaleziono użytkownika lub nieprawidłowe hasło'
        )
    keyring.set_password(SYS_NAME, user, password)
    click.echo(f'dane logowania użytkownika {user} zostały zapisane')


@cli.group(name='user', help='Zarządzanie użytkownikami')
def user_ops():
    pass


@user_ops.command(name='create', help='Zakładanie nowego konta użytkownika')
@click.option('--name', '-n', required=True, help='Nazwa konta użytkownika')
@click.password_option('--password', '-p', required=True, help='Hasło użytkownika')
@click.option('--email', '-e', required=False, help='Email użytkownika')
@click.option(
    '--active/--inactive', default=False,
    help='Czy konto ma być od razu aktywne (domyślnie: NIE)',
)
def user_create(name, password, email, active):
    user = User(
        name=name, password=pwd_context.hash(password), email=email, active=active
    )
    db.session.add(user)
    db.session.commit()
    click.echo(f'konto użytkownika {name} zostało założone')


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
    q = ObjectMenuItem.query
    if active is not None:
        q = q.filter(ObjectMenuItem.active.is_(active))
    for category in q.order_by(ObjectMenuItem.title).all():
        click.echo(category.title)


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
    password = keyring.get_password(SYS_NAME, user)
    if not password:
        password = click.prompt('Hasło: ', hide_input=True)
    user_obj = User.query.filter_by(name=user).first()
    if not (user_obj and pwd_context.verify(password, user_obj.password)):
        raise click.ClickException(
            'nieprawidłowe dane logowania - '
            'nie znaleziono użytkownika lub nieprawidłowe hasło'
        )
    keyring.set_password(SYS_NAME, user, password)
    c_page = SubjectPage(
        title=title, created_by=user_obj, active=active, text=title
    )
    c_dir = None
    if directory:
        c_dir = Directory(title=title, created_by=user_obj, active=active, page=c_page)
        db.session.add(c_dir)
    db.session.add(c_page)
    c_menuitem = ObjectMenuItem(
        directory=c_dir, page=c_page, title=title, active=active
    )
    db.session.add(c_menuitem)
    db.session.commit()
    click.echo(f'kategoria {title} została utworzona')


@cli.group(name='directory', help='Operacje na katalogach')
def directory_ops():
    pass


def main():
    load_dotenv(find_dotenv())
    cli()
