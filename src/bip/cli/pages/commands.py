import sys

import click
from flask import current_app
from flask.cli import with_appcontext

from ...display import ColumnOverride, DisplayMeta
from ...models import Page, Label
from ...utils.cli import ACTIVITY_NAME_MAP, ColDataType, create_table, print_table
from ...utils.text import truncate_string, yesno

page_ops = click.Group(name='page', help='Zarządzanie stronami biuletynu')


@page_ops.command(name='list', help='Wyświetl listę stron')
@click.option(
    '--active/--inactive', default=None,
    help='Wyświetl tylko aktywne lub nieaktywne (domyślnie: wszystkie)',
)
@with_appcontext
def page_list(active):
    page_prop = ACTIVITY_NAME_MAP[active]
    sort = [Page.title]
    q = Page.select()
    if active is not None:
        q = q.where(Page.active == active)
    q = q.order_by(*sort)
    page_count = q.count()
    if page_count == 0:
        click.echo('Nie ma żadnych stron')
        sys.exit(0)
    click.echo(f'Znaleziono: {page_count}, wyświetlanie: {page_prop}')
    col_overrides = {
        'pk': ColumnOverride(title='ID'),
        'title': ColumnOverride(title='Tytuł'),
        'active': ColumnOverride(title='Aktywna'),
        'labels': ColumnOverride(title='Etykiety', datatype=ColDataType.text)
    }
    col_names = ['pk', 'title', 'active', 'labels']
    columns = DisplayMeta(
        Page, columns=col_names
    ).cli_list_columns(overrides=col_overrides)
    table = create_table(current_app.testing, columns)
    for page_obj in q:
        labels = ', '.join([c.name for c in page_obj.labels(order=Label.name)])
        table.add_row([
            page_obj.pk, truncate_string(page_obj.title, 80), yesno(page_obj.active),
            labels,
        ])
    print_table(table)
