from dotenv import find_dotenv, load_dotenv
from flask.cli import FlaskGroup
from flask_migrate.cli import db as migrate_ops

from .. import make_app
from .database import commands as db_commands
from .users import commands as user_commands
from .pages import commands as page_commands

migrate_ops.help = 'Operacje na bazie danych aplikacji'


def create_app(_unused):  # pragma: no cover
    return make_app('dev')


cli = FlaskGroup(create_app=create_app, help='Zarządzanie aplikacją BIP')

cli.add_command(db_commands.migrate_ops, name='db')
cli.add_command(user_commands.user_ops)
cli.add_command(page_commands.page_ops)


def main():  # pragma: no cover
    load_dotenv(find_dotenv())
    cli()
