import click
from flask.cli import with_appcontext

from ...models import Attachment, ChangeRecord, Label, Page, PageLabel, User, db

db_ops = click.Group(name='db', help='Narzędzia bazy danych')

MODELS = [Attachment, ChangeRecord, Label, Page, PageLabel, User]


@db_ops.command(name='init', help='Initialize missing database objects')
@with_appcontext
def initdb():  # pragma: no cover
    db.create_tables(MODELS)


@db_ops.command(name='clear', help='Remove all database objects')
@with_appcontext
def cleardb():  # pragma: no cover
    db.drop_tables(MODELS)


@db_ops.command('recreate', help='Recreate all database objects from scratch')
@with_appcontext
def recreatedb():  # pragma: no cover
    db.drop_tables(MODELS)
    db.create_tables(MODELS)
