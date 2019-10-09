from flask.cli import with_appcontext
from flask_migrate.cli import db as migrate_ops

from ...ext import db


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
