from dotenv import find_dotenv, load_dotenv
from flask.cli import FlaskGroup

from .. import make_app
from .attachments import commands as attachment_commands
from .database import commands as db_commands
from .pages import commands as page_commands
from .users import commands as user_commands


def create_app(_unused):  # pragma: no cover
    return make_app('dev')


cli = FlaskGroup(create_app=create_app, help='Zarządzanie aplikacją BIP')

cli.add_command(db_commands.db_ops)
cli.add_command(user_commands.user_ops)
cli.add_command(page_commands.page_ops)
cli.add_command(page_commands.label_ops)
cli.add_command(attachment_commands.attachment_ops)


def main():  # pragma: no cover
    load_dotenv(find_dotenv())
    cli()
