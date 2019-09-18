import click
from dotenv import find_dotenv, load_dotenv
from flask.cli import FlaskGroup

from . import make_app
from .models import User, db
from .security import pwd_context


def create_app(info):
    return make_app('dev')


@click.group(
    cls=FlaskGroup, create_app=create_app, help='Zarządzanie aplikacją BIP'
)
def cli():
    pass


@cli.command('initdb', help='Initialize missing database objects')
def initdb():
    db.create_all()


@cli.command('cleardb', help='Remove all database objects')
def cleardb():
    db.drop_all()


@cli.command('recreatedb', help='Recreate all database objects from scratch')
def recreatedb():
    db.drop_all()
    db.create_all()


@cli.group(name='user', help='Zarządzanie użytkownikami')
def user_ops():
    pass


@user_ops.command(name='create', help='Zakładanie nowego konta użytkownika')
@click.option('--name', '-n', required=True, help='Nazwa konta użytkownika')
@click.password_option('--password', '-p', required=True, help='Hasło użytkownika')
@click.option('--email', '-e', required=False, help='Email użytkownika')
@click.option(
    '--active/--inactive', default=False, help='Czy konto ma być od razu aktywne'
)
def user_create(name, password, email, active):
    user = User(
        name=name, password=pwd_context.hash(password), email=email, active=active
    )
    db.session.add(user)
    db.session.commit()
    click.echo(f'konto użytkownika {name} zostało założone')


@cli.group(name='category', help='Zarządzanie kategoriami w menu')
def category_ops():
    pass


@category_ops.command(name='create', help='Utwórz nową kategorię w menu')
@click.option('--title', '-t', required=True, help='Tytuł kategorii')
@click.option(
    '--directory/--no-directory', default=False, help='Czy kategoria jest katalogiem'
)
@click.option(
    '--active/--inactive', default=False, help='Czy kategoria ma być od razu aktywna'
)
@click.option(
    '--order', '-o', type=int, default=None, help='Kolejność kategorii w menu'
)
@click.option(
    '--login', '-l', required=True,
    help='Zaloguj się do systemu jako wskazany użytkownik',
)
@click.option(
    '--password', '-p', prompt=True, hide_input=True, required=True,
    help='Hasło użytkownika',
)
def category_create(title, directory, active, order, login, password):
    user = User.query.filter_by(name=login).one()
    if not pwd_context.verify(password, user.password):
        raise click.ClickException('nieprawidłowe dane logowania')


def main():
    load_dotenv(find_dotenv())
    cli()
