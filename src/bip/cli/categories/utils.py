import click

from ...data import category


def check_category(pk, fail=True, message=None):
    obj = category.get(pk)
    if obj is None and fail:
        if message is None:
            message = 'Nie znaleziono kategorii o ID {pk}'
        raise click.ClickException(message.format(pk=pk))
    return obj


def check_parent(obj, parent_pk, fail=True):
    parent = check_category(
        parent_pk, message='Nie znaleziono kategorii nadrzędnej id ID {pk}'
    )
    if parent == obj and fail:
        raise click.ClickException(
            'Kategoria nie może być nadrzędna wobec samej siebie'
        )
    return parent
