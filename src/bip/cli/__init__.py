import click
from dotenv import find_dotenv, load_dotenv
from flask.cli import FlaskGroup
from flask_migrate.cli import db as migrate_ops

from .. import make_app
from .database import commands as db_commands
from .users import commands as user_commands
from .categories import commands as category_commands

migrate_ops.help = 'Operacje na bazie danych aplikacji'


def create_app(_unused):  # pragma: no cover
    return make_app('dev')


@click.group(
    cls=FlaskGroup, create_app=create_app, help='Zarządzanie aplikacją BIP'
)
def cli():  # pragma: no cover
    pass


cli.add_command(db_commands.migrate_ops, name='db')
cli.add_command(user_commands.user_ops)
cli.add_command(category_commands.category_ops)


def main():  # pragma: no cover
    load_dotenv(find_dotenv())
    cli()
