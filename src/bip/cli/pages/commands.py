import sys

import click
from flask import current_app
from flask.cli import with_appcontext

from ...data import Filter, Sort, page
from ...utils.cli import (
    ACTIVITY_NAME_MAP, ColAlign as ColA, ColDataType as ColDT, ColSpec, create_table,
    print_table,
)
from ...utils.text import truncate_string, yesno

page_ops = click.Group(name='page', help='Zarządzanie stronami kategorii i katalogów')


@page_ops.command(name='list', help='Wyświetl listę stron')
@click.option(
    '--active/--inactive', default=None,
    help='Wyświetl tylko aktywne lub nieaktywne (domyślnie: wszystkie)',
)
@with_appcontext
def page_list(active):
    page_prop = ACTIVITY_NAME_MAP[active]
    sort = [
        Sort('title')
    ]
    filters = None
    if active is not None:
        filters = [Filter(field='active', op='eq', value=active)]
    q = page.query(sort, filters)
    page_count = q.count()
    if page_count == 0:
        click.echo('Nie ma żadnych stron')
        sys.exit(0)
    click.echo(f'Znaleziono: {page_count}, wyświetlanie: {page_prop}')
    columns = [
        ColSpec(ColA.right, ColDT.int, 'ID'),
        ColSpec(ColA.left, ColDT.text, 'Tytuł'),
        ColSpec(ColA.center, ColDT.text, 'Aktywna'),
        ColSpec(ColA.left, ColDT.text, 'Kategorie'),
    ]
    table = create_table(current_app.testing, columns)
    for page_obj in q:
        categories = ', '.join([c.title for c in page_obj.categories])
        table.add_row([
            page_obj.pk, truncate_string(page_obj.title, 80), yesno(page_obj.active),
            categories,
        ])
    print_table(table)
