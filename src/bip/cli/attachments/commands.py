import sys

import click
from flask import current_app
from flask.cli import with_appcontext

from ...display import ColAlign, ColDataType, ColumnOverride, DisplayMeta
from ...models import Attachment, Page
from ...utils.cli import create_table, print_table
from ...utils.text import truncate_string

attachment_ops = click.Group(
    name='attachment', help='Zarządzanie załącznikami do stron'
)


@attachment_ops.command(name='list', help='Wyświetl listę załączników')
@with_appcontext
def attachment_list():
    q = Attachment.select().join(Page).order_by(Attachment.title)
    obj_count = q.count()
    if obj_count == 0:
        click.echo('Nie ma żadnych załączników')
        sys.exit(0)
    click.echo(f'Znaleziono: {obj_count}')
    col_overrides = {
        'pk': ColumnOverride(title='ID'),
        'title': ColumnOverride(title='Tytuł'),
        'file_type': ColumnOverride(title='Typ'),
        'page': ColumnOverride(
            title='Strona', datatype=ColDataType.text, align=ColAlign.left
        )
    }
    col_names = ['pk', 'title', 'file_type', 'page']
    columns = DisplayMeta(
        Attachment, columns=col_names
    ).cli_list_columns(overrides=col_overrides)
    table = create_table(current_app.testing, columns)
    for obj in q:
        page = truncate_string(obj.page.title, 80)
        table.add_row([obj.pk, truncate_string(obj.title, 80), obj.file_type, page])
    print_table(table)
