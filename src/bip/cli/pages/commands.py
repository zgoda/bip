import sys

import click
from flask import current_app
from flask.cli import with_appcontext
from markdown import markdown

from ...display import ColumnOverride, DisplayMeta
from ...models import Label, Page, PageLabel, db
from ...utils.cli import (
    ACTIVITY_NAME_MAP, ColDataType, create_table, login_user, print_table,
)
from ...utils.text import slugify, truncate_string, yesno

page_ops = click.Group(name='page', help='Zarządzanie stronami biuletynu')
label_ops = click.Group(name='label', help='Zarządzanie etykietami stron')


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
        labels = ', '.join([c.label.name for c in page_obj.labels(order=Label.name)])
        table.add_row([
            page_obj.pk, truncate_string(page_obj.title, 80), yesno(page_obj.active),
            labels,
        ])
    print_table(table)


@page_ops.command(name='create', help='Utwórz nową stronę')
@click.option('-t', '--title', required=True, help='Tytuł nowej strony')
@click.option(
    '--active/--inactive', default=False, help='Strona będzie aktywna (domyślnie: nie)'
)
@click.option(
    '--main/--not-main', default=False,
    help='Strona będzie miała pozycję w menu głównym (domyślnie: nie)',
)
@click.option(
    '-l', '--label', 'labels', multiple=True,
    help='Nadanie stronie etykiety, można użyć wielokrotnie',
)
@click.option(
    '-o', '--order', type=int, help='Ustalenie porządku strony w menu (domyślnie: brak)'
)
@click.option(
    '-u', '--user', 'user_name', required=True,
    help='Nazwa użytkownika który wykonuje operację',
)
@with_appcontext
def page_create(title, active, main, labels, order, user_name):
    actor = login_user(user_name, admin=False)
    text = click.edit()
    if not text:
        raise click.Abort('Tekst strony jest wymagany')
    description = None
    if click.confirm('Czy chcesz wprowadzić opis strony?', default=False):
        description = click.edit()
    label_objs = Label.select().where(Label.name << labels)
    with db.atomic():
        page = Page.create(
            title=title, slug=slugify(title), text=text, text_html=markdown(text),
            active=active, description=description, created_by=actor, updated_by=actor,
            main=main, order=order,
        )
        for label in label_objs:
            PageLabel.create(page=page, label=label)
    click.echo(f'strona {page.title} została utworzona')


@label_ops.command(name='list', help='Wyświetl listę etykiet')
@with_appcontext
def label_list():
    sort = [Label.name]
    q = Label.select().order_by(*sort)
    label_count = q.count()
    if label_count == 0:
        click.echo('Nie ma żadnych etykiet')
        sys.exit(0)
    click.echo(f'Znaleziono: {label_count}')
    col_overrides = {
        'pk': ColumnOverride(title='ID'),
        'name': ColumnOverride(title='Nazwa'),
    }
    col_names = ['pk', 'name']
    columns = DisplayMeta(
        Label, columns=col_names
    ).cli_list_columns(overrides=col_overrides)
    table = create_table(current_app.testing, columns)
    for label in q:
        table.add_row([label.pk, truncate_string(label.name, 80)])
    print_table(table)


@label_ops.command(name='create', help='Utwórz nową etykietę')
@click.option('--name', '-n', required=True, help='Nazwa etykiety')
@with_appcontext
def label_create(name):
    description = None
    if click.confirm('Czy chcesz wprowadzić opis etykiety?', default=True):
        description = click.edit()
    label = Label(name=name, slug=slugify(name))
    if description:
        label.description = description
        label.description_html = markdown(description)
    label.save()
    click.echo(f'etykieta {label.name} została utworzona')


@label_ops.command(name='change', help='Zmień istniejącą etykietę')
@click.option('--name', '-n', required=True, help='Nazwa etykiety')
@click.option('--new-name', help='Nowa nazwa dla etykiety')
@with_appcontext
def label_change(name, new_name):
    label = Label.get_or_none(Label.name == name)
    if label is None:
        raise click.Abort(f'etykieta {name} nie istnieje')
    if new_name is None:
        new_name = label.name
    change_desc = name == new_name
    new_description = label.description
    if click.confirm('Czy chcesz zmienić opis etykiety?', default=change_desc):
        new_description = click.edit(label.description)
    if new_description is None:
        new_description = label.description or ''
    new_description = new_description.strip()
    label.name = new_name
    label.slug = slugify(new_name)
    if new_description:
        label.description = new_description
        label.description_html = markdown(new_description)
    else:
        label.description = label.description_html = None
    label.save()
    click.echo(f'etykieta {name} została zmieniona')
