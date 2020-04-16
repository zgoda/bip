import sys

import click
from flask import current_app
from flask.cli import with_appcontext
from markdown import markdown

from ...display import ColumnOverride, DisplayMeta
from ...models import Change, ChangeRecord, Label, Page, PageLabel, db
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
        'order': ColumnOverride(title='Kolejność'),
        'labels': ColumnOverride(title='Etykiety', datatype=ColDataType.text)
    }
    col_names = ['pk', 'title', 'active', 'order', 'labels']
    columns = DisplayMeta(
        Page, columns=col_names
    ).cli_list_columns(overrides=col_overrides)
    table = create_table(current_app.testing, columns)
    for page_obj in q:
        labels = ', '.join(c.label.name for c in page_obj.labels(order=Label.name))
        table.add_row([
            page_obj.pk, truncate_string(page_obj.title, 80), yesno(page_obj.active),
            page_obj.order, labels,
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
        click.echo('Tekst strony jest wymagany')
        sys.exit(1)
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


@page_ops.command(name='change', help='Zmień wskazaną stronę')
@click.option('-i', '--id', 'page_id', required=True, help='ID strony', type=int)
@click.option(
    '-t', '--title', default=None, help='Nowy tytuł strony (domyślnie: bez zmiany)'
)
@click.option(
    '--active/--inactive', default=None,
    help='Strona będzie aktywna (domyślnie: bez zmiany)',
)
@click.option(
    '--main/--not-main', default=None,
    help='Strona będzie miała pozycję w menu głównym (domyślnie: bez zmiany)',
)
@click.option(
    '-o', '--order', type=int, default=None,
    help='Ustalenie porządku strony w menu (domyślnie: bez zmiany)',
)
@click.option(
    '-u', '--user', 'user_name', required=True,
    help='Nazwa użytkownika który wykonuje operację',
)
@with_appcontext
def page_change(page_id, title, active, main, order, user_name):
    actor = login_user(user_name, admin=False)
    with db.atomic():
        page = Page.get_by_id(page_id)
        if all([title is None, active is None, main is None, order is None]):
            click.echo(f'nie wprowadzono żadnych zmian strony {page.title}')
        else:
            changed = []
            if title is not None:
                page.title = title
                page.slug = slugify(title)
                changed.append('tytuł')
            if active is not None:
                page.active = active
                changed.append('aktywna')
            if main is not None:
                page.main = main
                changed.append('główna')
            if order is not None:
                page.order = order
                changed.append('kolejność')
            page.updated_by = actor
            page.save()
            changes = ', '.join(changed)
            desc = f'zmodyfikowana ({changes})'
            ChangeRecord.log_change(
                page=page, change_type=Change.updated, user=actor, description=desc
            )
            click.echo(f'strona {page.title} została zmieniona')


@page_ops.command(name='labels', help='Zmień etykiety wskazanej strony')
@click.option('-i', '--id', 'page_id', required=True, help='ID strony', type=int)
@click.option(
    '-o', '--operation', 'op', required=True,
    type=click.Choice(['add', 'replace'], case_sensitive=False),
    help='Rodzaj operacji, dodanie (add) lub zastąpienie (replace)',
)
@click.option(
    '-l', '--label', 'labels', multiple=True,
    help='Nadanie stronie etykiety, można użyć wielokrotnie',
)
@click.option(
    '-u', '--user', 'user_name', required=True,
    help='Nazwa użytkownika który wykonuje operację',
)
@with_appcontext
def page_labels(page_id, op, labels, user_name):
    actor = login_user(user_name, admin=False)
    op = op.lower()
    page = Page.get_by_id(page_id)
    if op == 'add':
        if not labels:
            click.echo(f'etykiety strony {page.title} nie zostały zmienione')
            sys.exit(0)
    change_args = {
        'page': page,
        'change_type': Change.updated,
        'user': actor,
        'description': 'zmodyfikowana (etykiety)',
    }
    label_objs = Label.select().where(Label.name << labels)
    if label_objs.count() != len(labels) and not click.confirm(
        'nie wszystkie etykiety zostały znalezione, kontyuować?'
    ):
        click.echo('operacja zmiany etykiet strony przerwana')
        sys.exit(0)
    with db.atomic():
        if op == 'replace':
            PageLabel.delete().where(PageLabel.page == page).execute()
        for label in label_objs:
            PageLabel.create(page=page, label=label)
        ChangeRecord.log_change(**change_args)
        click.echo(f'etykiety strony {page.title} zostały zaktualizowane')


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
